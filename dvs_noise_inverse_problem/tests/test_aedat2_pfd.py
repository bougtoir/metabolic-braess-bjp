"""Smoke tests for the AEDAT-2.0 reader and the PFD comparator (no data download)."""
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sp_evaluation as sp
from aedat2 import read_aedat2


def _write_aedat2(path, addrs, ts):
    with open(path, 'wb') as f:
        f.write(b'#!AER-DAT2.0\r\n# comment\r\n')
        f.writelines(struct.pack('>II', a, t) for a, t in zip(addrs, ts))


def _addr(x, y, p):
    return (y << 22) | (x << 12) | (p << 11)


def test_decode_and_skip_aps(tmp_path):
    p = tmp_path / 'a.aedat'
    addrs = [_addr(5, 7, 1), (1 << 31) | 123, _addr(300, 200, 0)]
    _write_aedat2(p, addrs, [10, 11, 12])
    ev = read_aedat2(p)
    assert len(ev) == 2
    assert (ev['x'].tolist(), ev['y'].tolist(), ev['p'].tolist()) == ([5, 300], [7, 200], [1, 0])
    assert ev['t'].tolist() == [10, 12]


def test_timestamp_rollover_and_reset(tmp_path):
    p = tmp_path / 'b.aedat'
    a = _addr(1, 1, 1)
    # 32-bit wrap near 2^32, then a logger reset to 1
    ts = [(1 << 32) - 5, (1 << 32) - 1, 3, 10, 1, 4]
    _write_aedat2(p, [a] * len(ts), ts)
    ev = read_aedat2(p)
    t = ev['t']
    assert np.all(np.diff(t) >= 0)
    assert t[2] == (1 << 32) + 3
    assert t[4] == t[3] + 1 and t[5] == t[3] + 4


def test_pfd_filter_prefers_supported_events():
    rng = np.random.default_rng(0)
    H, W = 40, 40
    n_noise = 400
    noise = np.empty(n_noise, dtype=[('x', '<i8'), ('y', '<i8'), ('t', '<i8'), ('p', '<i8')])
    noise['x'] = rng.integers(0, W, n_noise)
    noise['y'] = rng.integers(0, H, n_noise)
    noise['t'] = np.sort(rng.integers(0, 1_000_000, n_noise))
    noise['p'] = rng.integers(0, 2, n_noise)
    # a compact moving edge: same polarity, 3x3 cluster every 1 ms
    sig = []
    for k in range(60):
        for dx in range(3):
            for dy in range(3):
                sig.append((10 + k // 4 + dx, 20 + dy, 100_000 + k * 1000 + dx * 10 + dy, 1))
    sig = np.array(sig, dtype=noise.dtype)
    ev = np.concatenate([noise, sig])
    lab = np.r_[np.zeros(n_noise, bool), np.ones(len(sig), bool)]
    order = np.argsort(ev['t'], kind='stable')
    ev, lab = ev[order], lab[order]
    p_noise = sp.pfd_filter(ev, (H, W))
    assert p_noise.shape == (len(ev),)
    assert np.all((p_noise >= 0) & (p_noise <= 1))
    assert p_noise[lab].mean() < p_noise[~lab].mean()
