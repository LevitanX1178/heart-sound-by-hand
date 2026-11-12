"""Zero-phase filtering by hand: lfilter (Direct Form II transposed), steady-state start, odd padding, forward-backward = filtfilt.

Everything is a loop you can follow with a pencil. The Excel workbook 01_filtfilt/filtfilt_by_hand.xlsx does the same, cell by cell.
"""
import numpy as np


def lfilter_df2t(b, a, x, zi=None):
    """y[n] = b0 x[n] + z1;  z1' = b1 x[n] - a1 y[n] + z2;  z2' = b2 x[n] - a2 y[n]   (second order; any order works)."""
    b = np.asarray(b, float); a = np.asarray(a, float); b = b / a[0]; a = a / a[0]; n = max(len(a), len(b))
    b = np.r_[b, np.zeros(n - len(b))]; a = np.r_[a, np.zeros(n - len(a))]
    z = np.zeros(n - 1) if zi is None else np.array(zi, float)
    y = np.empty(len(x))
    for i, xi in enumerate(x):
        y[i] = b[0] * xi + z[0]
        for k in range(n - 2): z[k] = b[k + 1] * xi - a[k + 1] * y[i] + z[k + 1]
        z[n - 2] = b[n - 1] * xi - a[n - 1] * y[i]
    return y


def zi_second_order(b, a):
    """Steady-state start for a second-order section, closed form.  G = DC gain.  z2 = b2 - a2 G ;  z1 = b1 + b2 - (a1 + a2) G."""
    b0, b1, b2 = b; a0, a1, a2 = a; G = (b0 + b1 + b2) / (a0 + a1 + a2)
    return np.array([b1 + b2 - (a1 + a2) * G, b2 - a2 * G])


def lfilter_zi(b, a):
    """General steady-state start (solve (I - A) zi = B), the same idea for any order."""
    b = np.asarray(b, float); a = np.asarray(a, float); b = b / a[0]; a = a / a[0]; n = max(len(a), len(b))
    b = np.r_[b, np.zeros(n - len(b))]; a = np.r_[a, np.zeros(n - len(a))]
    comp = np.zeros((n - 1, n - 1)); comp[0, :] = -a[1:]; comp[1:, :-1] = np.eye(n - 2)
    return np.linalg.solve(np.eye(n - 1) - comp.T, b[1:] - a[1:] * b[0])


def odd_extension(x, padlen):
    """Mirror the signal around its end points so the filter does not see a jump: left = 2 x[0] - x[padlen..1]."""
    return np.concatenate([2 * x[0] - x[padlen:0:-1], x, 2 * x[-1] - x[-2:-padlen - 2:-1]])


def filtfilt_by_hand(b, a, x, padlen=None):
    """Forward, flip, backward, flip. Delay of the forward pass is undone by the backward pass: zero phase, and the magnitude is squared."""
    x = np.asarray(x, float); padlen = 3 * max(len(a), len(b)) if padlen is None else padlen
    ext = odd_extension(x, padlen); zi = lfilter_zi(b, a)
    y = lfilter_df2t(b, a, ext, zi * ext[0])            # 1. forward
    y = y[::-1]                                          # 2. flip
    y = lfilter_df2t(b, a, y, zi * y[0])                 # 3. filter again, now backward in time
    y = y[::-1]                                          # 4. flip back
    return y[padlen:len(y) - padlen]
