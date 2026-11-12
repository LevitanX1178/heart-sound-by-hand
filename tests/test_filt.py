import numpy as np
from scipy.signal import butter, filtfilt, lfilter, lfilter_zi as sp_zi
from hsbh.filt import lfilter_df2t, lfilter_zi, zi_second_order, filtfilt_by_hand, odd_extension

def _sig(n=200, seed=0): return np.random.default_rng(seed).standard_normal(n).cumsum()

def test_lfilter_matches_scipy():
    b, a = butter(2, 25, 'high', fs=500); x = _sig()
    assert np.allclose(lfilter_df2t(b, a, x), lfilter(b, a, x), atol=1e-10)

def test_steady_state_start_three_ways_agree():
    b, a = butter(2, 25, 'high', fs=500)
    assert np.allclose(zi_second_order(b, a), sp_zi(b, a), atol=1e-12) and np.allclose(lfilter_zi(b, a), sp_zi(b, a), atol=1e-12)

def test_filtfilt_matches_scipy_highpass_and_bandpass():
    for b, a in (butter(2, 25, 'high', fs=500), butter(2, [25, 100], 'band', fs=500), butter(4, 40, 'low', fs=500)):
        for seed in range(3):
            x = _sig(300, seed); assert np.max(np.abs(filtfilt_by_hand(b, a, x) - filtfilt(b, a, x))) < 1e-9

def test_zero_phase_peak_does_not_move():
    t = np.arange(400) / 500; x = np.exp(-((t - 0.4) / 0.02) ** 2); b, a = butter(2, [10, 120], 'band', fs=500)
    assert np.argmax(filtfilt_by_hand(b, a, x)) == np.argmax(x)                       # zero phase
    assert np.argmax(lfilter_df2t(b, a, x)) != np.argmax(x)                           # one forward pass moves it (here 5 samples EARLIER: a high-pass part leads in phase)

def test_odd_extension_shape_and_ends():
    x = np.arange(10.0); e = odd_extension(x, 3); assert len(e) == 16 and e[3] == x[0] and e[-4] == x[-1]
