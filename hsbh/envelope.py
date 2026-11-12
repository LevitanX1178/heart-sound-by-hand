"""Envelope by hand: Hilbert amplitude (FIR version), Gaussian smoothing kernel, power mean.

Mirrors the project's power_mean_envelope: smooth(a ** p) ** (1 / p) with a Gaussian of sigma = 0.1325 / fc * fs samples.
(0.1325 = sqrt(ln 2) / (2 pi): the Gaussian whose amplitude response is down 3 dB at fc.)
"""
import numpy as np


def hilbert_fir(x, half=15):
    """Hilbert transform as a short convolution:  H(x)[n] = sum over odd m of 2/(pi m) * x[n - m],  |m| <= half.  Edge samples are NaN (no full window).
    A truncated filter is an approximation: with half = 15 the amplitude is within about 1-5% of scipy.signal.hilbert in the heart-sound band (more taps, less error). Use scipy in practice."""
    x = np.asarray(x, float); y = np.full(len(x), np.nan); ms = [m for m in range(-half, half + 1) if m % 2 != 0]
    for n in range(half, len(x) - half): y[n] = sum(2.0 / (np.pi * m) * x[n - m] for m in ms)
    return y


def amplitude_fir(x, half=15):
    """Analytic amplitude sqrt(x^2 + H(x)^2) with the FIR Hilbert transform."""
    x = np.asarray(x, float); return np.sqrt(x ** 2 + hilbert_fir(x, half) ** 2)


def sigma_samples(fc, fs): return 0.1325 / fc * fs


def gaussian_kernel(sigma, radius=None):
    radius = int(4.0 * sigma + 0.5) if radius is None else radius; k = np.arange(-radius, radius + 1); w = np.exp(-0.5 * (k / sigma) ** 2); return w / w.sum()


def gaussian_smooth(y, sigma, radius=None):
    """Weighted average of neighbours; the ends are mirrored (same rule as scipy.ndimage.gaussian_filter1d, mode='reflect')."""
    w = gaussian_kernel(sigma, radius); r = len(w) // 2; yp = np.pad(np.asarray(y, float), r, mode='symmetric'); return np.convolve(yp, w, mode='valid')


def power_mean_envelope(a, fs, p, fc, floor=0.001):
    """(Gaussian-smoothed a^p)^(1/p). p = 1 is the plain average. A smaller p compresses large values before averaging, so one loud peak counts for less inside each local average (p -> 0 is the geometric mean); p = 2 lets peaks dominate.
    On the synthetic clip of module 2 the effect is small (murmur-to-S1 ratio 0.337, 0.327, 0.315 for p = 2, 1, 0.25). Why the project uses 0.25 comes from tuning on PhysioNet, which this repository does not repeat."""
    a = np.maximum(np.asarray(a, float), floor * float(np.max(a)) + 1e-12); return gaussian_smooth(a ** p, sigma_samples(fc, fs)) ** (1.0 / p)
