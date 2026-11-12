# Module 2 exercises

1. **One Hilbert value.** In the workbook, click `C57`. Write the eight products on paper and add them. Compare.
2. **Why odd j?** The weights are `2/(pi j)` for odd `j` and zero for even `j`. Compute the transform of a constant signal and of a sine at fs/4 by hand. What should each give?
3. **Gaussian weights.** Check that the weights in column M add to 1 and that the weight at k = 0 is the largest. Change `fc` to 6 Hz and describe what happens to sigma, the weights and the envelope.
4. **Power mean by hand.** For the three values 0.05, 1.0, 0.05, compute the power mean (equal weights) for p = 2, 1 and 0.25. Which is largest? Which is closest to the geometric mean?
5. **Explore p.** Using `hsbh.synth.make_pcg` with `murmur_level` 0.03, 0.08 and 0.25 and different noise, compute the murmur-to-S1 ratio for p = 2, 1, 0.25. Is there any setting where the smaller p raises it? Report what you find.
6. **Approximation.** Run `amplitude_fir` with `half` = 7, 15 and 31 on a 30 Hz and an 80 Hz sine and tabulate the error against `scipy.signal.hilbert`.
