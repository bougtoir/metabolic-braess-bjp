"""Minimal reader for jAER AEDAT-2.0 files recorded with DAVIS240/346 chips.

Only DVS events are returned (APS and IMU samples are discarded).  The
address encoding follows the jAER ``DavisBaseCamera`` layout: bit 31 selects
APS/IMU (1) versus DVS (0), bits 22-30 hold y, bits 12-21 hold x and bit 11
holds the polarity.
"""

import numpy as np

EVENT_DTYPE = np.dtype([('x', '<u2'), ('y', '<u2'), ('t', '<i8'), ('p', '<u1')])


def read_aedat2(path, max_events=None):
    with open(path, 'rb') as f:
        header_end = 0
        while True:
            pos = f.tell()
            line = f.readline()
            if not line.startswith(b'#'):
                header_end = pos
                break
        f.seek(header_end)
        raw = np.frombuffer(f.read(), dtype='>u4')
    if raw.size % 2:
        raw = raw[:-1]
    addr = raw[0::2]
    ts = raw[1::2].astype(np.int64)
    dvs = (addr >> 31) == 0
    addr = addr[dvs]
    ts = ts[dvs]
    # jAER timestamps may wrap (32-bit rollover) or be reset by the logger
    # during a recording; both appear as a large negative jump and are
    # unwrapped so that the stream is monotone.
    for w in np.flatnonzero(np.diff(ts) < 0):
        jump = ts[w] - ts[w + 1]
        ts[w + 1:] += (1 << 32) if jump > (1 << 30) and ts[w] > (1 << 31) else jump + 1
    ev = np.empty(addr.size, dtype=EVENT_DTYPE)
    ev['y'] = (addr >> 22) & 0x1FF
    ev['x'] = (addr >> 12) & 0x3FF
    ev['p'] = (addr >> 11) & 1
    ev['t'] = ts
    if max_events is not None and ev.size > max_events:
        ev = ev[:max_events]
    return ev
