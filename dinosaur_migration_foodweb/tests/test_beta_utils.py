import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from beta_utils import mean_beta, pairwise_simpson, pairwise_sorensen


def test_identical_assemblages_zero_turnover():
    mat = np.array([[1, 1, 0], [1, 1, 0]])
    assert pairwise_simpson(mat)[0, 1] == 0.0
    assert pairwise_sorensen(mat)[0, 1] == 0.0


def test_disjoint_assemblages_full_turnover():
    mat = np.array([[1, 0], [0, 1]])
    assert pairwise_simpson(mat)[0, 1] == 1.0
    assert pairwise_sorensen(mat)[0, 1] == 1.0


def test_simpson_insensitive_to_richness():
    # {a} vs {a,b}: nested difference -> Simpson turnover 0, Sorensen > 0
    mat = np.array([[1, 0], [1, 1]])
    assert pairwise_simpson(mat)[0, 1] == 0.0
    assert pairwise_sorensen(mat)[0, 1] > 0.0


def test_mean_beta():
    mat = np.array([[1, 0], [0, 1], [1, 0]])
    d = pairwise_simpson(mat)
    assert abs(mean_beta(d) - (1.0 + 0.0 + 1.0) / 3) < 1e-9
