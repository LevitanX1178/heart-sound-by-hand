"""Module 4 experiment: (a) does the quality score prefer the doubled cycle? (b) does the half-cycle test catch it, and when does it fail?
Run:  python 04_doubled_cycle/experiment.py      (about a minute).  Synthetic recordings, so the true cycle length T is known."""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from hsbh.synth import make_pcg; from hsbh.pipeline import envelope_50hz; from hsbh.cycle import autocorr, quality, pair_sums, half_cycle_ratio

N, TH = 120, 0.8; MUR = [None, 'systolic', 'holosystolic', 'diastolic']; rows = []
for seed in range(N):
    rng = np.random.default_rng(seed); hr = rng.uniform(50, 95); cv = rng.uniform(0.04, 0.15); mur = MUR[seed % 4]
    d = make_pcg(hr=hr, dur=20, cv=cv, murmur=mur, seed=seed); L = d['cycle_len']; T = 60 / hr
    fooled = quality(pair_sums(L), 20.0) > quality(L, 20.0)
    r = autocorr(envelope_50hz(d['x'], d['fs']), 110)
    def near(i): w = range(max(1, i - 3), min(len(r) - 2, i + 3) + 1); return max(w, key=lambda l: r[l])
    iT, i2 = near(int(round(T * 50))), int(round(2 * T * 50)); i2 = near(i2) if i2 <= 108 else None
    rows.append(dict(mur=str(mur), fooled=fooled, ratioT=half_cycle_ratio(r, iT), ratio2T=half_cycle_ratio(r, i2) if i2 else np.nan))
print(f'{N} synthetic recordings, threshold {TH} (a teaching choice, not tuned)\n')
print(f'{"murmur":14s} {"quality prefers 2T":>20s} {"2T flagged (hit)":>18s} {"T flagged (false alarm)":>24s}')
for m in [str(x) for x in MUR]:
    rr = [x for x in rows if x['mur'] == m]
    print(f'{m:14s} {np.mean([x["fooled"] for x in rr]):20.2f} {np.nanmean([x["ratio2T"] > TH for x in rr]):18.2f} {np.mean([x["ratioT"] > TH for x in rr]):24.2f}')
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures'), exist_ok=True)
fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
for m, c in zip([str(x) for x in MUR], ['#555', '#2b6cb0', '#c05621', '#2f855a']):
    rr = [x for x in rows if x['mur'] == m]; ax[0].scatter(np.full(len(rr), MUR.index(None if m == 'None' else m)) + np.random.default_rng(0).uniform(-.15, .15, len(rr)), [x['ratioT'] for x in rr], s=8, color=c)
    ax[1].scatter(np.full(len(rr), MUR.index(None if m == 'None' else m)) + np.random.default_rng(1).uniform(-.15, .15, len(rr)), [x['ratio2T'] for x in rr], s=8, color=c)
for a_, t_ in zip(ax, ['correct period T: ratio r(T/2)/r(T)', 'doubled period 2T: ratio r(T)/r(2T)']):
    a_.axhline(TH, color='k', ls='--', lw=1); a_.set_xticks(range(4)); a_.set_xticklabels(['none', 'systolic', 'holosys.', 'diastolic'], fontsize=8); a_.set_title(t_, fontsize=9); a_.set_ylim(-1.5, 3)
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures', 'doubled_cycle_test.png'), dpi=160); print('figure: figures/doubled_cycle_test.png')
