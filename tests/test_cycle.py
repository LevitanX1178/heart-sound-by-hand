import numpy as np
from hsbh.synth import make_pcg
from hsbh.pipeline import envelope_50hz
from hsbh.cycle import autocorr, top_periods, quality, pair_sums, half_cycle_ratio

def test_autocorr_matches_numpy():
    x = np.random.default_rng(0).standard_normal(300); r = autocorr(x, 60); xc = x - x.mean(); full = np.correlate(xc, xc, 'full')[len(x) - 1:] / np.sum(xc ** 2)
    assert np.allclose(r, full[:61], atol=1e-12)

def test_synthetic_truth_is_ordered():
    d = make_pcg(seed=3); assert np.all(d['s2'] > d['s1']) and np.all(d['s1'][1:] > d['s2'][:-1]) and len(d['s1']) >= 8

def test_cycle_length_found_on_clean_synthetic():
    for hr in (55, 70, 90):
        d = make_pcg(hr=hr, dur=20, cv=0.03, seed=hr); r = autocorr(envelope_50hz(d['x'], d['fs']), 110); T, _ = top_periods(r, 50)[0]
        assert abs(T - 60 / hr) / (60 / hr) < 0.06 or abs(T - 2 * 60 / hr) / (2 * 60 / hr) < 0.06      # the strongest peak is T or 2T

def test_pair_sums_have_smaller_cv_for_independent_beats():
    rng = np.random.default_rng(1); ratios = []
    for _ in range(300):
        L = 1.0 * (1 + 0.13 * rng.standard_normal(40)); P = pair_sums(L); ratios.append((P.std() / P.mean()) / (L.std() / L.mean()))
    assert abs(np.mean(ratios) - 1 / np.sqrt(2)) < 0.07

def test_quality_prefers_the_doubled_cycle_when_beats_vary_independently():
    wins = 0
    for s in range(50):
        d = make_pcg(dur=20, cv=0.10, seed=s); L = d['cycle_len']; wins += quality(pair_sums(L), 20.0) > quality(L, 20.0)
    assert wins >= 45
