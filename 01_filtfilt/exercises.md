# Module 1 exercises

1. **Trace one sample.** In the workbook, click `E16`. Write the formula in words. Then compute `E17` with a calculator from `B16`, `B17`, `C17`, the coefficients, and compare.
2. **No padding.** Set `pad` to 0 conceptually: take the first filtered values and explain, in two sentences, why the start would ring. (Compare the forward-only column with the filtfilt column in the first 5 rows.)
3. **Zero phase.** In `tests/test_filt.py::test_zero_phase_peak_does_not_move` the single forward pass moves the peak 5 samples *earlier*, not later. Why can a band-pass filter make a peak earlier? (Hint: think of the high-pass part, which leads in phase.)
4. **Squared magnitude.** For a second-order Butterworth, one pass is -3 dB at the cut-off. What is filtfilt at the cut-off in dB? What does that do to your choice of cut-off frequency?
5. **Closed form.** Show on paper that `zi2 = b2 - a2 G` follows from the state equations when the input and the output are constant.
6. **Real time.** A stethoscope sends one sample every 0.5 ms. Describe in three sentences how you would filter it with one forward pass and what delay you accept. Compute the group delay of your filter near 60 Hz with `scipy.signal.group_delay`.
7. **Break it.** Change one coefficient by 1% in the workbook. Which output differs most, and why?
