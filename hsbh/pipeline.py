"""The chain used in the later modules: band-pass (zero-phase) -> Hilbert amplitude -> power-mean envelope -> 50 Hz envelope for the cycle search.
Library calls are used here on purpose (scipy); modules 1 and 2 show what each call does, by hand, and the tests prove they agree."""
import numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert, resample_poly
from .envelope import power_mean_envelope


def envelope_50hz(x, fs, p=0.25, fc=12.0, band=(25.0, 400.0)):
    sos = butter(4, band, btype='band', fs=fs, output='sos'); xb = sosfiltfilt(sos, x)
    return resample_poly(power_mean_envelope(np.abs(hilbert(xb)), fs, p, fc), 1, int(fs // 50))
