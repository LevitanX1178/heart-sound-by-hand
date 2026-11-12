"""A synthetic heart sound with KNOWN S1 and S2 times, so any step can be scored against the truth.

The sounds are damped sine bursts (S1 ~55 Hz, S2 ~80 Hz). The S1-to-S2 gap follows 0.131 + 0.225 T (T = cycle length), a rough
physiological relation (the same shape the project's fixed_tempo decoder uses). A murmur is band-limited noise shaped in time.
"""
import numpy as np
from scipy.signal import butter, sosfilt


def _burst(x, t, t0, f, decay, amp):
    m = t >= t0
    x[m] += amp * np.exp(-(t[m] - t0) / decay) * np.sin(2 * np.pi * f * (t[m] - t0))


def make_pcg(hr=64.0, dur=10.0, fs=1000, cv=0.05, murmur=None, murmur_level=0.3, noise=0.01, drift=0.3, hum=0.02, seed=0):
    """Return dict(x, fs, s1, s2, T0, cycle_len): signal and true event times (seconds).

    murmur: None | 'systolic' (diamond shaped, S1 to S2) | 'holosystolic' (flat) | 'diastolic' (S2 to next S1, fading).
    cv: beat-to-beat variation of the cycle length (std / mean).
    """
    rng = np.random.default_rng(seed)
    n = int(dur * fs); t = np.arange(n) / fs; x = np.zeros(n); T0 = 60.0 / hr
    s1, s2, lens = [], [], []; tc = 0.3
    while tc < dur - 0.7:
        T = max(0.4, T0 * (1 + cv * rng.standard_normal())); lens.append(T)
        s1.append(tc); s2.append(tc + 0.131 + 0.225 * T); tc += T
    sos = butter(4, [100, 350], btype='band', fs=fs, output='sos'); mur = sosfilt(sos, rng.standard_normal(n)); mur /= mur.std()
    shape = np.zeros(n)
    for i, a in enumerate(s1):
        b = s2[i]; nxt = s1[i + 1] if i + 1 < len(s1) else min(dur, a + lens[i])
        _burst(x, t, a, 55, 0.030, 1.0); _burst(x, t, a, 90, 0.020, 0.4); _burst(x, t, b, 80, 0.020, 0.7); _burst(x, t, b, 120, 0.015, 0.25)
        if murmur in ('systolic', 'holosystolic'):
            i0, i1 = int((a + 0.04) * fs), int((b - 0.02) * fs)
            if i1 > i0: shape[i0:i1] = np.hanning(i1 - i0) if murmur == 'systolic' else 1.0
        elif murmur == 'diastolic':
            i0, i1 = int((b + 0.04) * fs), int((nxt - 0.03) * fs)
            if i1 > i0: shape[i0:i1] = np.exp(-np.linspace(0, 3, i1 - i0))
    if murmur: x += murmur_level * shape * mur
    x += noise * rng.standard_normal(n) + drift * np.sin(2 * np.pi * 0.4 * t + 1.0) + hum * np.sin(2 * np.pi * 50 * t)
    return dict(x=x, fs=fs, s1=np.array(s1), s2=np.array(s2), T0=T0, cycle_len=np.array(lens))
