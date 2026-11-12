"""Builds the four Excel workbooks (live formulas) for modules 1-4. Run from the repository root:  python tools/build_workbooks.py"""
import os, sys
import numpy as np
from math import pi
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, ScatterChart, Reference, Series
from openpyxl.utils import get_column_letter as CL
from scipy.signal import butter, filtfilt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); sys.path.insert(0, ROOT)
from hsbh.synth import make_pcg; from hsbh.pipeline import envelope_50hz; from hsbh.cycle import autocorr, pair_sums, quality, local_peaks
from hsbh.envelope import hilbert_fir, sigma_samples, gaussian_kernel

F = 'Arial'
f_n = Font(name=F, size=10); f_b = Font(name=F, size=10, bold=True); f_t = Font(name=F, size=14, bold=True, color='1F3864'); f_s = Font(name=F, size=10, italic=True, color='595959')
f_in = Font(name=F, size=10, color='0000FF'); f_h = Font(name=F, size=10, bold=True, color='FFFFFF'); f_g = Font(name=F, size=10, color='808080')
fl_h = PatternFill('solid', fgColor='1F3864'); fl_in = PatternFill('solid', fgColor='FFF2CC'); fl_k = PatternFill('solid', fgColor='E2EFDA'); fl_e = PatternFill('solid', fgColor='EDEDED')
th = Side(style='thin', color='BFBFBF'); box = Border(left=th, right=th, top=th, bottom=th)

def new(title):
    wb = Workbook(); ws = wb.active; ws.title = title; ws.sheet_view.showGridLines = False; return wb, ws
def put(ws, ref, v, font=f_n, fmt=None, fill=None, wrap=False, align=None, border=True):
    c = ws[ref]; c.value = v; c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if border: c.border = box
    c.alignment = Alignment(wrap_text=wrap, vertical='center', horizontal=align); return c
def head(ws, row, col, labels, height=None):
    for i, t in enumerate(labels): put(ws, f'{CL(col + i)}{row}', t, f_h, fill=fl_h, wrap=True, align='center')
    if height: ws.row_dimensions[row].height = height
def note(ws, ref, t, font=f_s, to=None, h=None):
    c = ws[ref]; c.value = t; c.font = font; c.alignment = Alignment(wrap_text=True, vertical='top')
    if to: ws.merge_cells(f'{ref}:{to}')
    if h: ws.row_dimensions[c.row].height = h
def inp(ws, ref, v, fmt=None): return put(ws, ref, v, f_in, fmt, fl_in)
def widths(ws, d):
    for k, v in d.items(): ws.column_dimensions[k].width = v
def save(wb, rel):
    wb.calculation.fullCalcOnLoad = True; p = os.path.join(ROOT, rel); wb.save(p); print('saved', rel)

# ======================================================================================= 1. filtfilt
FS1, N1, PAD = 500, 40, 9
b1, a1 = butter(2, 25, 'high', fs=FS1); t1 = np.arange(N1) / FS1
x1 = 1.0 + 8 * t1 + np.where(t1 >= 0.03, 0.9 * np.exp(-(t1 - 0.03) / 0.01) * np.sin(2 * pi * 60 * (t1 - 0.03)), 0.0); x1 = np.round(x1, 4)
ref1 = filtfilt(b1, a1, x1)
wb, ws = new('filtfilt'); widths(ws, {'A': 7, 'B': 11, 'C': 11, 'D': 11, 'E': 11, 'F': 11, 'G': 11, 'H': 11, 'I': 11, 'J': 11, 'K': 3, 'L': 3, 'M': 3, 'N': 6, 'O': 10, 'P': 14, 'Q': 14, 'R': 12, 'S': 14})
note(ws, 'A1', 'Module 1: zero-phase filtering (filtfilt) by hand', f_t, 'J1', 24)
note(ws, 'A2', 'A 2nd-order Butterworth high-pass (25 Hz, fs = 500 Hz) removes the slow drift under a heart sound. Forward pass, flip, backward pass, flip: the shift of the forward pass is undone by the backward pass. '
     'Blue-on-yellow cells are inputs. Every other cell is a formula: click it.', f_s, 'S2', 32)
for i, (lab, v) in enumerate([('b0', b1[0]), ('b1', b1[1]), ('b2', b1[2]), ('a1', a1[1]), ('a2', a1[2])]): put(ws, f'A{5 + i}', lab, f_b); inp(ws, f'B{5 + i}', float(v), '0.000000')
note(ws, 'C5', 'Filter coefficients (a0 = 1) from scipy.signal.butter(2, 25, "high", fs=500). Module 2 of the roadmap derives them by hand.', f_s, 'J6', 28)
put(ws, 'A10', 'G', f_b); put(ws, 'B10', '=(B5+B6+B7)/(1+B8+B9)', fmt='0.000000'); note(ws, 'C10', 'DC gain: output for a constant input (0 for a high-pass)', f_s, 'J10')
put(ws, 'A11', 'zi1', f_b); put(ws, 'B11', '=B6+B7-(B8+B9)*B10', fmt='0.000000', fill=fl_k); note(ws, 'C11', 'start-up state: the state the filter would have if the input had been constant forever', f_s, 'J11')
put(ws, 'A12', 'zi2', f_b); put(ws, 'B12', '=B7-B9*B10', fmt='0.000000', fill=fl_k); note(ws, 'C12', 'we start each pass from zi x (first sample), so there is no jump at the edge', f_s, 'J12')
put(ws, 'A13', 'N', f_b); inp(ws, 'B13', N1); put(ws, 'A14', 'pad', f_b); inp(ws, 'B14', PAD); note(ws, 'C13', 'N samples; pad = how many mirrored samples are added at each end (scipy uses 3 x filter length = 9)', f_s, 'J14')
head(ws, 15, 1, ['k', 'padded x', 'state z1', 'state z2', 'forward y', 'flipped y', 'state z1', 'state z2', 'backward y', 'flipped back'], 32)
M = N1 + 2 * PAD; R0 = 16; RL = R0 + M - 1; XR = f'$O${R0}:$O${R0 + N1 - 1}'
for k in range(1, M + 1):
    r = R0 + k - 1; put(ws, f'A{r}', k)
    put(ws, f'B{r}', f'=IF(A{r}<=$B$14,2*INDEX({XR},1)-INDEX({XR},$B$14-A{r}+2),IF(A{r}<=$B$14+$B$13,INDEX({XR},A{r}-$B$14),2*INDEX({XR},$B$13)-INDEX({XR},2*$B$13+$B$14-A{r})))', fmt='0.0000', fill=fl_e if (k <= PAD or k > PAD + N1) else None)
    if k == 1: put(ws, f'C{r}', f'=$B$11*B{r}', fmt='0.0000'); put(ws, f'D{r}', f'=$B$12*B{r}', fmt='0.0000')
    else: put(ws, f'C{r}', f'=$B$6*B{r - 1}-$B$8*E{r - 1}+D{r - 1}', fmt='0.0000'); put(ws, f'D{r}', f'=$B$7*B{r - 1}-$B$9*E{r - 1}', fmt='0.0000')
    put(ws, f'E{r}', f'=$B$5*B{r}+C{r}', fmt='0.0000', fill=fl_k)
    put(ws, f'F{r}', f'=INDEX($E${R0}:$E${RL},{M + 1}-A{r})', fmt='0.0000')
    if k == 1: put(ws, f'G{r}', f'=$B$11*F{r}', fmt='0.0000'); put(ws, f'H{r}', f'=$B$12*F{r}', fmt='0.0000')
    else: put(ws, f'G{r}', f'=$B$6*F{r - 1}-$B$8*I{r - 1}+H{r - 1}', fmt='0.0000'); put(ws, f'H{r}', f'=$B$7*F{r - 1}-$B$9*I{r - 1}', fmt='0.0000')
    put(ws, f'I{r}', f'=$B$5*F{r}+G{r}', fmt='0.0000', fill=fl_k); put(ws, f'J{r}', f'=INDEX($I${R0}:$I${RL},{M + 1}-A{r})', fmt='0.0000')
head(ws, 15, 14, ['n', 'x (input)', 'filtfilt by hand', 'scipy filtfilt (static)', 'difference', 'forward pass only'], 32)
for n in range(N1):
    r = R0 + n; put(ws, f'N{r}', n); inp(ws, f'O{r}', float(x1[n]), '0.0000'); put(ws, f'P{r}', f'=INDEX($J${R0}:$J${RL},N{r}+$B$14+1)', fmt='0.0000', fill=fl_k)
    put(ws, f'Q{r}', float(ref1[n]), f_in, '0.0000'); put(ws, f'R{r}', f'=P{r}-Q{r}', fmt='0.0E+00'); put(ws, f'S{r}', f'=INDEX($E${R0}:$E${RL},N{r}+$B$14+1)', fmt='0.0000')
put(ws, f'N{R0 + N1 + 1}', 'largest |difference|', f_b, border=False); put(ws, f'R{R0 + N1 + 1}', f'=MAX(MAX(R{R0}:R{R0 + N1 - 1}),-MIN(R{R0}:R{R0 + N1 - 1}))', fmt='0.0E+00', fill=fl_k)
note(ws, f'N{R0 + N1 + 3}', 'The difference is at the level of rounding error (about 1e-15). The same check is run in Python by tests/test_filt.py.', f_s, f'S{R0 + N1 + 4}', 30)
lc = LineChart(); lc.title = 'Input, forward pass only, and filtfilt'; lc.height = 8; lc.width = 15; lc.y_axis.delete = False; lc.x_axis.delete = False
for col in (15, 16, 19): lc.add_data(Reference(ws, min_col=col, min_row=15, max_row=R0 + N1 - 1), titles_from_data=True)
lc.set_categories(Reference(ws, min_col=14, min_row=R0, max_row=R0 + N1 - 1)); ws.add_chart(lc, 'U4'); ws.freeze_panes = 'A16'
# ---- first sheet: the four steps on 8 numbers (a first-order filter), so a beginner starts small
sh = wb.create_sheet('start_here', 0); sh.sheet_view.showGridLines = False; widths(sh, {'A': 26, 'B': 14, 'C': 14, 'D': 14, 'E': 14, 'F': 14, 'G': 3, 'H': 70})
note(sh, 'A1', 'Start here: filtfilt in four steps on 8 numbers', f_t, 'F1', 24)
note(sh, 'A2', 'A filter with memory: output = m x (previous output) + (1 - m) x input. Blue-on-yellow cells are inputs: change them. Everything else is a formula: click it.', f_s, 'F2', 30)
put(sh, 'A4', 'memory m (0 to 0.9)', f_b); inp(sh, 'B4', 0.5, '0.0')
head(sh, 6, 1, ['n (position)', 'x: input', '1. forward', '2. flipped', '3. filter again', '4. flipped back'], 32)
for n in range(8):
    r = 7 + n; put(sh, f'A{r}', n); inp(sh, f'B{r}', 4 if n == 3 else 0, '0.00')
    put(sh, f'C{r}', f'=(1-$B$4)*B{r}' if n == 0 else f'=$B$4*C{r - 1}+(1-$B$4)*B{r}', fmt='0.000', fill=fl_k)
    put(sh, f'D{r}', f'=INDEX($C$7:$C$14,8-A{r})', fmt='0.000')
    put(sh, f'E{r}', f'=(1-$B$4)*D{r}' if n == 0 else f'=$B$4*E{r - 1}+(1-$B$4)*D{r}', fmt='0.000', fill=fl_k)
    put(sh, f'F{r}', f'=INDEX($E$7:$E$14,8-A{r})', fmt='0.000', fill=fl_k)
head(sh, 16, 1, ['check', 'forward only', 'after filtfilt'], 20)
put(sh, 'A17', 'sum left of spike (n 0 to 2)', f_b); put(sh, 'B17', '=SUM(C7:C9)', fmt='0.000'); put(sh, 'C17', '=SUM(F7:F9)', fmt='0.000')
put(sh, 'A18', 'sum right of spike (n 4 to 6)', f_b); put(sh, 'B18', '=SUM(C11:C13)', fmt='0.000'); put(sh, 'C18', '=SUM(F11:F13)', fmt='0.000')
put(sh, 'A19', 'tallest bar at n =', f_b); put(sh, 'B19', '=MATCH(MAX(C7:C14),C7:C14,0)-1', fmt='0'); put(sh, 'C19', '=MATCH(MAX(F7:F14),F7:F14,0)-1', fmt='0')
note(sh, 'A21', 'Forward only: all the smear is on the right (left sum is 0). After filtfilt: smear on both sides, nearly equal, and the tallest bar is still at n = 3. That is zero phase.', f_s, 'F21', 44)
steps = ['DO THIS, IN ORDER', '1. Click C7. Read the formula: (1 - m) x input, because there is no earlier output yet.', '2. Click C8. Read it: m x (output above) + (1 - m) x input. Work out C10 on paper with m = 0.5 (answer: 2), then check.',
         '3. Fill in column C on paper for all 8 rows, then compare with the sheet.', '4. Click D7. It takes column C from the bottom up (the flip). Check that D7 is the last value of column C.',
         '5. Column E repeats the rule of column C, now on the flipped list. Column F flips it back.', '6. Change m (B4) to 0.8. Predict first: will the smear get longer or shorter? Then look.',
         '7. Move the spike: type 4 in B8 and 0 in B10. What happens to the left sum and the right sum?', '8. When this is clear, open the sheet filtfilt: the same four steps with a 2nd-order filter and 40 real samples.']
for i, t in enumerate(steps): c = sh[f'H{4 + i}']; c.value = t; c.font = f_b if i == 0 else f_n; c.alignment = Alignment(wrap_text=True, vertical='top'); sh.row_dimensions[4 + i].height = 30 if i else 18
bc = LineChart(); bc.title = 'input, forward only, filtfilt'; bc.height = 7; bc.width = 13; bc.y_axis.delete = False; bc.x_axis.delete = False
for col in (2, 3, 6): bc.add_data(Reference(sh, min_col=col, min_row=6, max_row=14), titles_from_data=True)
bc.set_categories(Reference(sh, min_col=1, min_row=7, max_row=14)); sh.add_chart(bc, 'A23'); wb.active = 0
save(wb, '01_filtfilt/filtfilt_by_hand.xlsx')
EXPECT1 = (ref1, x1)

# ======================================================================================= 2. envelope
FS2, N2, FC2, HALF = 250, 100, 12.0, 15
rng = np.random.default_rng(5); t2 = np.arange(N2) / FS2
x2 = np.where(t2 >= 0.04, np.exp(-(t2 - 0.04) / 0.03) * np.sin(2 * pi * 40 * (t2 - 0.04)), 0.0) + np.where(t2 >= 0.16, 0.12 * rng.standard_normal(N2) * np.exp(-(t2 - 0.16) / 0.15), 0.0) + 0.01 * rng.standard_normal(N2)
x2 = np.round(x2, 4); sig2 = sigma_samples(FC2, FS2); RAD = int(4 * sig2 + 0.5)
wb, ws = new('envelope'); widths(ws, {'A': 6, 'B': 10, 'C': 11, 'D': 11, 'E': 11, 'F': 11, 'G': 11, 'H': 12, 'I': 12, 'J': 12, 'K': 3, 'L': 8, 'M': 12, 'N': 12})
note(ws, 'A1', 'Module 2: envelope by hand (Hilbert amplitude, power mean, Gaussian smoothing)', f_t, 'J1', 24)
note(ws, 'A2', 'Step 1: Hilbert transform as a short sum with weights 2/(pi j). Step 2: amplitude = sqrt(x^2 + H^2). Step 3: raise to the power p, smooth with a Gaussian, take the p-th root. '
     'A small p compresses big values before averaging, so one loud peak counts for less in each local average; a large p lets peaks dominate. Compare the three envelope columns and the chart.', f_s, 'N2', 34)
put(ws, 'A4', 'fs', f_b); inp(ws, 'B4', FS2); put(ws, 'C4', 'fc', f_b); inp(ws, 'D4', FC2); put(ws, 'E4', 'sigma', f_b); put(ws, 'F4', '=0.1325/D4*B4', fmt='0.000', fill=fl_k)
note(ws, 'G4', 'sigma (in samples) = 0.1325 / fc x fs. The Gaussian is down 3 dB at fc = 12 Hz.', f_s, 'N4', 28)
put(ws, 'L6', 'j', f_b); put(ws, 'M6', 'h = 2/(pi j)', f_b)
for i, j in enumerate(range(1, HALF + 1, 2)): put(ws, f'L{7 + i}', j); put(ws, f'M{7 + i}', f'=2/(PI()*L{7 + i})', fmt='0.0000')
put(ws, 'L16', 'k', f_b); put(ws, 'M16', 'Gaussian weight', f_b)
for i, k in enumerate(range(-RAD, RAD + 1)): put(ws, f'L{17 + i}', k); put(ws, f'M{17 + i}', f'=EXP(-0.5*(L{17 + i}/$F$4)^2)/SUMPRODUCT(EXP(-0.5*($L$17:$L${17 + 2 * RAD}/$F$4)^2))', fmt='0.0000')
KR = f'$M$17:$M${17 + 2 * RAD}'
head(ws, 6, 1, ['n', 'x (band-passed)', 'H(x)', 'amplitude', 'a^p1', 'a^p2', 'a^p3', 'envelope p1', 'envelope p2', 'envelope p3'], 32)
put(ws, 'A5', 'p', f_b)
for col, p in zip('EFG', (2.0, 1.0, 0.25)): inp(ws, f'{col}5', p)
for col, src in zip('HIJ', 'EFG'): put(ws, f'{col}5', f'={src}5', fmt='0.00')
R0 = 7; floor = 'MAX($D$%d:$D$%d)*0.001' % (R0 + HALF, R0 + N2 - HALF - 1)
for n in range(N2):
    r = R0 + n; put(ws, f'A{r}', n); inp(ws, f'B{r}', float(x2[n]), '0.0000')
    if HALF <= n <= N2 - HALF - 1:
        terms = '+'.join(f'$M${7 + i}*(B{r - j}-B{r + j})' for i, j in enumerate(range(1, HALF + 1, 2)))
        put(ws, f'C{r}', '=' + terms, fmt='0.0000'); put(ws, f'D{r}', f'=SQRT(B{r}^2+C{r}^2)', fmt='0.0000', fill=fl_k)
        for col, pc in zip('EFG', 'EFG'): put(ws, f'{col}{r}', f'=MAX(D{r},{floor})^{pc}$5', fmt='0.0000')
    else:
        for col in 'CDEFG': put(ws, f'{col}{r}', None, fill=fl_e)
    if HALF + RAD <= n <= N2 - HALF - 1 - RAD:
        for col, src in zip('HIJ', 'EFG'): put(ws, f'{col}{r}', f'=SUMPRODUCT({KR},{src}{r - RAD}:{src}{r + RAD})^(1/{col}$5)', fmt='0.0000', fill=fl_k)
    else:
        for col in 'HIJ': put(ws, f'{col}{r}', None, fill=fl_e)
note(ws, f'A{R0 + N2 + 1}', 'Grey cells are edges where the window does not fit. Python (hsbh/envelope.py) mirrors the ends instead; here we simply skip them to keep every formula identical.', f_s, f'J{R0 + N2 + 2}', 30)
lc = LineChart(); lc.title = 'Three envelopes of the same clip (p = 2, 1, 0.25)'; lc.height = 8; lc.width = 16; lc.y_axis.delete = False; lc.x_axis.delete = False
for col in (8, 9, 10): lc.add_data(Reference(ws, min_col=col, min_row=6, max_row=R0 + N2 - 1), titles_from_data=True)
lc.set_categories(Reference(ws, min_col=1, min_row=R0, max_row=R0 + N2 - 1)); ws.add_chart(lc, 'O4'); ws.freeze_panes = 'A7'
save(wb, '02_envelope/envelope_by_hand.xlsx')
EXPECT2 = dict(x=x2, fs=FS2, fc=FC2, half=HALF, rad=RAD)

# ======================================================================================= 3. autocorrelation
d3 = make_pcg(hr=62.5, dur=8, cv=0.04, murmur='systolic', seed=11, fs=1000); e3 = np.round(envelope_50hz(d3['x'], d3['fs']), 4); N3 = len(e3); LAGS = list(range(10, 111))
r3 = autocorr(e3, 110); T3 = float(np.mean(d3['cycle_len']))
wb, ws = new('autocorr'); widths(ws, {'A': 7, 'B': 11, 'C': 11, 'D': 3, 'E': 7, 'F': 9, 'G': 12, 'H': 14, 'I': 12, 'J': 14, 'K': 3, 'L': 20, 'M': 12, 'N': 12})
note(ws, 'A1', 'Module 3: the cycle length from autocorrelation, by hand', f_t, 'N1', 24)
note(ws, 'A2', 'The envelope of 8 s of (synthetic) heart sound, 50 values per second. For each lag l, multiply the envelope by itself shifted by l samples and add up: a big r(l) means "shifted by l looks like the original". '
     f'The true mean cycle length is {T3:.3f} s ({T3 * 50:.1f} samples), so expect peaks near lag 48 (T) and 96 (2T) and a dip near 24 (T/2).', f_s, 'N2', 44)
put(ws, 'A4', 'N', f_b); put(ws, 'B4', f'=COUNT(B8:B{7 + N3})'); put(ws, 'A5', 'mean', f_b); put(ws, 'B5', f'=AVERAGE(B8:B{7 + N3})', fmt='0.0000'); put(ws, 'A6', 'D', f_b); put(ws, 'B6', f'=SUMSQ(C8:C{7 + N3})', fmt='0.0000')
note(ws, 'C4', 'D = sum of squared deviations (the same sum at lag 0). r(l) = sum of products at lag l / D.', f_s, 'J6', 28)
head(ws, 7, 1, ['t', 'envelope', 'x - mean'])
for i in range(N3): r = 8 + i; put(ws, f'A{r}', i); inp(ws, f'B{r}', float(e3[i]), '0.0000'); put(ws, f'C{r}', f'=B{r}-$B$5', fmt='0.0000')
head(ws, 7, 5, ['lag', 'seconds', 'r(lag) by hand', 'numpy (static)', 'difference', 'peak? (value)'], 32)
RL = 7 + N3
for i, l in enumerate(LAGS):
    r = 8 + i; put(ws, f'E{r}', l); put(ws, f'F{r}', f'=E{r}/50', fmt='0.00')
    put(ws, f'G{r}', f'=SUMPRODUCT(C8:C{RL - l},C{8 + l}:C{RL})/$B$6', fmt='0.0000', fill=fl_k); put(ws, f'H{r}', float(r3[l]), f_in, '0.0000'); put(ws, f'I{r}', f'=G{r}-H{r}', fmt='0.0E+00')
    if i == 0 or i == len(LAGS) - 1: put(ws, f'J{r}', None, fill=fl_e)
    else: put(ws, f'J{r}', f'=IF(AND(E{r}>=18,E{r}<=100,G{r}>G{r - 1},G{r}>=G{r + 1}),G{r},"")', fmt='0.0000')
LR = 7 + len(LAGS); PK = f'$J$8:$J${LR}'
put(ws, 'L7', 'strongest peaks in 0.35 to 2.0 s', f_h, fill=fl_h, wrap=True); put(ws, 'M7', 'period (s)', f_h, fill=fl_h); put(ws, 'N7', 'r', f_h, fill=fl_h)
for k in range(1, 4):
    r = 7 + k; put(ws, f'L{r}', f'peak {k}', f_b); put(ws, f'N{r}', f'=LARGE({PK},{k})', fmt='0.000', fill=fl_k); put(ws, f'M{r}', f'=INDEX($F$8:$F${LR},MATCH(N{r},{PK},0))', fmt='0.00', fill=fl_k)
put(ws, 'L12', 'largest |difference| to numpy', f_b, wrap=True); put(ws, 'N12', f'=MAX(MAX(I8:I{LR}),-MIN(I8:I{LR}))', fmt='0.0E+00', fill=fl_k)
note(ws, 'L14', 'The three strongest peaks are candidate cycle lengths. Typically the true T and 2T both appear, and the search must choose. That choice is Module 4.', f_s, 'N17', 60)
sc = ScatterChart(); sc.title = 'Autocorrelation r(l): peaks at T and 2T'; sc.style = 13; sc.height = 8; sc.width = 15; sc.x_axis.title = 'lag (s)'; sc.y_axis.title = 'r'; sc.y_axis.delete = False; sc.x_axis.delete = False
s_ = Series(Reference(ws, min_col=7, min_row=8, max_row=LR), Reference(ws, min_col=6, min_row=8, max_row=LR), title='r(lag)'); s_.marker.symbol = 'none'; sc.series.append(s_); ws.add_chart(sc, 'L19'); ws.freeze_panes = 'A8'
save(wb, '03_cycle_length/autocorr_by_hand.xlsx')

# ======================================================================================= 4. doubled cycle
Z = np.round(np.random.default_rng(21).standard_normal(20), 3)
def near(i): return max(range(i - 3, i + 4), key=lambda l: r3[l])
nomT = int(round(T3 * 50)); iT, iH, i2 = near(nomT // 2), near(nomT), near(2 * nomT)
wb, ws = new('quality_gate'); widths(ws, {'A': 26, 'B': 14, 'C': 14, 'D': 14, 'E': 3, 'F': 8, 'G': 12, 'H': 12, 'I': 8, 'J': 12})
note(ws, 'A1', 'Module 4: why a quality score can prefer the doubled cycle', f_t, 'J1', 24)
note(ws, 'A2', 'Hypothesis A reads every heartbeat as one cycle. Hypothesis B reads two neighbouring beats as one cycle (a doubled cycle). The quality score is coverage x regularity x plausibility, and regularity = 1 / (1 + (CV / 0.12)^2). '
     'Change the beat-to-beat variation s and watch which hypothesis wins. Beat lengths here are T x (1 + s x z) with fixed random z.', f_s, 'J2', 46)
put(ws, 'A4', 'mean beat T (s)', f_b); inp(ws, 'B4', 0.96, '0.00'); put(ws, 'A5', 'beat-to-beat variation s', f_b); inp(ws, 'B5', 0.13, '0.00'); put(ws, 'A6', 'recording length (s)', f_b); inp(ws, 'B6', 20, '0'); put(ws, 'A7', 'CV scale cv0', f_b); inp(ws, 'B7', 0.12, '0.00'); put(ws, 'A8', 'gate', f_b); inp(ws, 'B8', 0.35, '0.00')
head(ws, 10, 1, ['', 'A: single beats', 'B: pairs of beats'], 20)
rows = [('number of cycles', '=COUNT(G5:G24)', '=COUNT(J5:J14)', '0'), ('mean cycle (s)', '=AVERAGE(G5:G24)', '=AVERAGE(J5:J14)', '0.000'), ('std dev (s)', '=STDEVP(G5:G24)', '=STDEVP(J5:J14)', '0.000'), ('CV = std / mean', '=B13/B12', '=C13/C12', '0.000'),
        ('coverage = sum / length', '=MIN(1,SUM(G5:G24)/$B$6)', '=MIN(1,SUM(J5:J14)/$B$6)', '0.000'), ('regularity', '=1/(1+(B14/$B$7)^2)', '=1/(1+(C14/$B$7)^2)', '0.000'), ('plausibility (systole share ok)', 1, 1, '0.0'),
        ('QUALITY', '=B15*B16*B17', '=C15*C16*C17', '0.000'), ('passes the gate?', '=IF(B18>=$B$8,"yes","no")', '=IF(C18>=$B$8,"yes","no")', None)]
for i, (lab, fa, fb, fmt) in enumerate(rows):
    r = 11 + i; put(ws, f'A{r}', lab, f_b); put(ws, f'B{r}', fa, fmt=fmt, fill=fl_k if lab in ('QUALITY', 'CV = std / mean') else None); put(ws, f'C{r}', fb, fmt=fmt, fill=fl_k if lab in ('QUALITY', 'CV = std / mean') else None)
put(ws, 'A21', 'which wins?', f_b); put(ws, 'B21', '=IF(C18>B18,"B (doubled) wins","A (single beats) wins")', f_b, fill=fl_k); ws.merge_cells('B21:C21')
put(ws, 'A22', 'CV of B expected = CV of A / sqrt(2)', f_b); put(ws, 'B22', '=B14/SQRT(2)', fmt='0.000'); put(ws, 'C22', '=C14', fmt='0.000')
note(ws, 'A24', 'Why: if each beat varies independently, adding two beats averages part of the variation away, so the relative spread (CV) of the pairs is smaller by about 1/sqrt(2). A smaller CV means a higher regularity, so the score rises. '
     'Both hypotheses cover the same recording and pass the gate. The gate asks "is it regular and complete?", never "is the cycle length right?". Real hearts have correlated beat-to-beat variation, so the effect in a real recording is weaker; '
     'in recording MR_011 of the project the CVs were 0.131 (19 cycles) against 0.109 (9 cycles), the same direction.', f_s, 'D30', 90)
head(ws, 4, 6, ['k', 'z (fixed draw)', 'beat A (s)', '', 'pair B (s)'], 32)
for k in range(20):
    r = 5 + k; put(ws, f'F{r}', k + 1); inp(ws, f'H{r}', float(Z[k]), '0.000'); put(ws, f'G{r}', f'=$B$4*(1+$B$5*H{r})', fmt='0.000')
# fix column order: F k, G beat, H z, I blank, J pair
head(ws, 4, 6, ['k', 'beat A (s)', 'z (fixed draw)', '', 'pair B (s)'], 32)
for j in range(10): r = 5 + j; put(ws, f'J{r}', f'=G{5 + 2 * j}+G{6 + 2 * j}', fmt='0.000', fill=fl_k)
ws2 = wb.create_sheet('half_cycle_test'); ws2.sheet_view.showGridLines = False; widths(ws2, {'A': 34, 'B': 14, 'C': 14, 'D': 14, 'E': 14})
note(ws2, 'A1', 'The half-cycle test: does the signal at half the period look as alike as at the period itself?', f_t, 'E1', 24)
note(ws2, 'A2', 'ratio = r(P/2) / r(P), with r the autocorrelation from Module 3. For a true cycle P, the half-cycle is a different part of the heartbeat (S1 is not S2, systole is not diastole), so r(P/2) is low and the ratio is small. '
     'For a doubled P (= 2T), P/2 is one whole beat, so r(P/2) is as high as r(P) and the ratio is near 1 or above. If ratio > threshold, call P doubled and use P/2.', f_s, 'E2', 60)
put(ws2, 'A4', 'threshold', f_b); inp(ws2, 'B4', 0.8, '0.00'); note(ws2, 'C4', 'a teaching choice, not tuned', f_s, 'E4')
head(ws2, 6, 1, ['candidate period P', 'r(P/2)', 'r(P)', 'ratio'], 20)
put(ws2, 'A7', f'P = T (lag {iH})', f_b); inp(ws2, 'B7', float(r3[iT]), '0.000'); inp(ws2, 'C7', float(r3[iH]), '0.000'); put(ws2, 'D7', '=B7/C7', fmt='0.00', fill=fl_k)
put(ws2, 'A8', f'P = 2T (lag {i2})', f_b); inp(ws2, 'B8', float(r3[iH]), '0.000'); inp(ws2, 'C8', float(r3[i2]), '0.000'); put(ws2, 'D8', '=B8/C8', fmt='0.00', fill=fl_k)
put(ws2, 'E6', 'verdict', f_h, fill=fl_h, align='center'); put(ws2, 'E7', '=IF(D7>$B$4,"doubled","accept")', f_b, fill=fl_k); put(ws2, 'E8', '=IF(D8>$B$4,"doubled","accept")', f_b, fill=fl_k)
note(ws2, 'A10', f'Values from the same synthetic recording as Module 3 (systolic murmur, seed 11), read at the autocorrelation peaks near lags {iT}, {iH} and {i2}.', f_s, 'E10', 30)
note(ws2, 'A12', 'How well does it work? 120 synthetic recordings (python 04_doubled_cycle/experiment.py), threshold 0.8. Static numbers:', f_b, 'E12', 20)
head(ws2, 13, 1, ['murmur', 'quality prefers 2T', '2T flagged (hit)', 'T flagged (false alarm)'], 32)
for i, row in enumerate([('none', 1.00, 0.73, 0.00), ('systolic', 1.00, 0.83, 0.00), ('holosystolic', 1.00, 0.97, 0.00), ('diastolic', 0.97, 0.93, 0.47)]):
    put(ws2, f'A{14 + i}', row[0], f_b)
    for j in range(3): put(ws2, f'{"BCD"[j]}{14 + i}', row[j + 1], f_in, '0.00')
note(ws2, 'A19', 'Reading: the quality score prefers the doubled cycle almost always when beats vary independently. The half-cycle test catches most doubled cycles and almost never rejects a correct one, EXCEPT with diastolic murmurs, '
     'where it rejects a correct period in 47% of recordings. Why? A diastolic murmur fills the gap after S2 and makes the two halves of the cycle alike. This is an open question for you (see exercises.md). '
     'It matters: aortic regurgitation and mitral stenosis are the diastolic diseases.', f_s, 'E19', 90)
save(wb, '04_doubled_cycle/doubled_cycle_by_hand.xlsx')
EXPECT4 = dict(z=Z, iT=iT, iH=iH, i2=i2, r3=r3)
