import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import hilbert
from hsbh.envelope import hilbert_fir, amplitude_fir, gaussian_smooth, sigma_samples, power_mean_envelope

def test_gaussian_matches_scipy():
    y = np.random.default_rng(0).random(120)
    for s in (1.5, 2.76, 5.0): assert np.allclose(gaussian_smooth(y, s), gaussian_filter1d(y, s, mode='reflect'), atol=1e-12)

def test_sigma_constant_is_the_3db_gaussian():
    assert abs(0.1325 - np.sqrt(np.log(2)) / (2 * np.pi)) < 1e-4

def test_hilbert_fir_close_to_fft_hilbert_in_band():
    fs = 250; t = np.arange(400) / fs
    for f in (50, 80):
        x = np.sin(2 * np.pi * f * t) * np.hanning(400); ref = np.abs(hilbert(x)); a = amplitude_fir(x, 15)
        m = ~np.isnan(a); assert np.max(np.abs(a[m] - ref[m])) < 0.04 * ref.max()

def test_power_mean_p1_is_plain_smooth():
    a = np.r_[np.ones(40) * 0.05, np.ones(10) * 1.0, np.ones(40) * 0.05]
    assert np.allclose(power_mean_envelope(a, 250, 1.0, 12.0), gaussian_smooth(np.maximum(a, 0.001 * a.max() + 1e-12), sigma_samples(12.0, 250)), atol=1e-9)

def test_smaller_p_counts_a_single_loud_spike_for_less():
    a = np.full(101, 0.05); a[50] = 1.0
    top = lambda p: power_mean_envelope(a, 250, p, 12.0)[50]
    assert top(0.25) < top(1.0) < top(2.0)
