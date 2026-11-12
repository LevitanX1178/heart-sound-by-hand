"""Cycle length by autocorrelation, the quality score, and the doubled-cycle problem."""
import numpy as np


def autocorr(x, max_lag):
    """r[l] = sum (x[t]-m)(x[t+l]-m) / sum (x[t]-m)^2 : how much the envelope looks like itself shifted by l samples (r[0] = 1)."""
    x = np.asarray(x, float) - np.mean(x); d = float(np.sum(x * x)); r = np.empty(max_lag + 1); r[0] = 1.0
    for l in range(1, max_lag + 1): r[l] = float(np.sum(x[:-l] * x[l:])) / d
    return r


def local_peaks(r, lo, hi):
    """Lags l in [lo, hi] with r[l-1] < r[l] >= r[l+1]."""
    return [l for l in range(max(lo, 1), min(hi, len(r) - 2) + 1) if r[l] > r[l - 1] and r[l] >= r[l + 1]]


def top_periods(r, fs_env, lo_s=0.35, hi_s=2.0, k=3):
    """The k strongest autocorrelation peaks inside the allowed cycle range: candidate cycle lengths in seconds, strongest first."""
    pk = local_peaks(r, int(round(lo_s * fs_env)), int(round(hi_s * fs_env))); pk.sort(key=lambda l: -r[l]); return [(l / fs_env, float(r[l])) for l in pk[:k]]


def quality(cycle_lens, rec_len, plausibility=1.0, cv0=0.12):
    """The project's quality score: coverage x regularity x plausibility. regularity = 1 / (1 + (CV / cv0)^2), CV = std / mean of the cycle lengths."""
    L = np.asarray(cycle_lens, float)
    if len(L) < 2: return 0.0
    cov = min(1.0, L.sum() / rec_len); cv = L.std() / L.mean(); return float(cov * (1.0 / (1.0 + (cv / cv0) ** 2)) * plausibility)


def pair_sums(lens):
    """What a doubled cycle is made of: two neighbouring beats added together (non-overlapping pairs)."""
    L = np.asarray(lens, float); n = len(L) // 2 * 2; return L[:n].reshape(-1, 2).sum(1)


def half_cycle_ratio(r, P_idx):
    """r(P/2) / r(P). Close to 1 means the signal at half the period looks as alike as at the period itself, so P is probably two beats."""
    return float(r[P_idx // 2] / r[P_idx])
