"""Draws the figures used in the module READMEs. Run from the repository root: python tools/make_figures.py"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from math import pi
from scipy.signal import butter, sosfiltfilt, hilbert
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); sys.path.insert(0, ROOT)
from hsbh.synth import make_pcg; from hsbh.filt import filtfilt_by_hand, lfilter_df2t; from hsbh.envelope import power_mean_envelope
from hsbh.pipeline import envelope_50hz; from hsbh.cycle import autocorr, quality, pair_sums
plt.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False}); FD = os.path.join(ROOT, 'figures'); os.makedirs(FD, exist_ok=True)

# 1. filtfilt: one pass moves the peak, filtfilt does not
fs = 500; t = np.arange(400) / fs; x = 0.5 * np.sin(2 * pi * 0.8 * t) + np.exp(-((t - 0.4) / 0.02) ** 2); b, a = butter(2, [10, 120], 'band', fs=fs)
f1 = lfilter_df2t(b, a, x); f2 = filtfilt_by_hand(b, a, x)
fig, ax = plt.subplots(figsize=(6.5, 2.6)); ax.plot(t, x, color='#999', label='input (drift + one sound)'); ax.plot(t, f1, color='#c05621', label='one forward pass: peak moves'); ax.plot(t, f2, color='#2b6cb0', label='filtfilt by hand: peak stays')
ax.axvline(t[np.argmax(np.exp(-((t - 0.4) / 0.02) ** 2))], color='k', ls=':', lw=1); ax.legend(frameon=False, fontsize=7); ax.set_xlabel('time (s)'); fig.tight_layout(); fig.savefig(os.path.join(FD, 'm1_filtfilt.png'), dpi=170); plt.close(fig)

# 2. envelope: p = 2, 1, 0.25 on a clip with a systolic murmur
d = make_pcg(hr=64, dur=4, cv=0.03, murmur='systolic', murmur_level=0.25, seed=2); sos = butter(4, [25, 400], 'band', fs=d['fs'], output='sos'); amp = np.abs(hilbert(sosfiltfilt(sos, d['x']))); tt = np.arange(len(amp)) / d['fs']
fig, ax = plt.subplots(figsize=(6.5, 2.6))
for p, c in ((2.0, '#c05621'), (1.0, '#555'), (0.25, '#2b6cb0')): e = power_mean_envelope(amp, d['fs'], p, 12.0); ax.plot(tt, e / np.percentile(e, 99), color=c, label=f'p = {p}')
for s in d['s1']: ax.axvline(s, color='#bbb', lw=0.6)
ax.set_xlim(0, 3.2); ax.set_xlabel('time (s); grey lines = true S1'); ax.legend(frameon=False); ax.set_title('three values of p give similar envelopes on this clip (murmur / S1 ratio 0.34, 0.33, 0.32 for p = 2, 1, 0.25)', fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FD, 'm2_envelope.png'), dpi=170); plt.close(fig)

# 3. autocorrelation of the module-3 envelope
d3 = make_pcg(hr=62.5, dur=8, cv=0.04, murmur='systolic', seed=11); e3 = envelope_50hz(d3['x'], d3['fs']); r = autocorr(e3, 110); lag = np.arange(111) / 50
fig, ax = plt.subplots(figsize=(6.5, 2.6)); ax.plot(lag, r, color='#2b6cb0')
for L, nm in ((0.48, 'T/2'), (0.96, 'T'), (1.92, '2T')): ax.axvline(L, color='#c05621', ls=':', lw=1); ax.text(L, 0.78, nm, ha='center', color='#c05621')
ax.set_xlabel('lag (s)'); ax.set_ylabel('r(lag)'); ax.set_ylim(-0.7, 0.9); fig.tight_layout(); fig.savefig(os.path.join(FD, 'm3_autocorr.png'), dpi=170); plt.close(fig)

# 4. quality of single beats vs pairs, as the beat-to-beat variation grows
rng = np.random.default_rng(0); S = np.linspace(0.02, 0.25, 16); qa, qb = [], []
for s in S:
    A, B = [], []
    for _ in range(300): L = 0.96 * (1 + s * rng.standard_normal(20)); A.append(quality(L, 20.0)); B.append(quality(pair_sums(L), 20.0))
    qa.append(np.mean(A)); qb.append(np.mean(B))
fig, ax = plt.subplots(figsize=(6.5, 2.6)); ax.plot(S, qa, color='#2b6cb0', label='A: single beats (correct)'); ax.plot(S, qb, color='#c05621', label='B: pairs of beats (doubled)'); ax.axhline(0.35, color='k', ls='--', lw=1); ax.text(0.02, 0.37, 'gate 0.35', fontsize=7)
ax.set_xlabel('beat-to-beat variation s (std / mean)'); ax.set_ylabel('quality'); ax.legend(frameon=False); ax.set_title('independent beats: the doubled cycle always scores higher', fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FD, 'm4_quality.png'), dpi=170); plt.close(fig)
print('figures written to', FD)
