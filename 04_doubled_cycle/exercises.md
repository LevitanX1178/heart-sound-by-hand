# Module 4 exercises

1. **Reproduce the effect.** In the workbook, set `s` to 0.05, 0.13 and 0.25. For each, write which hypothesis wins and the two quality values. Find the value of `s` above which A (correct) fails the 0.35 gate while B (doubled) still passes: a doubled cycle accepted where the correct one is rejected. Compare with the figure in the README.
2. **Derive `1/sqrt(2)`.** Prove that for two independent beats with mean `T` and standard deviation `sT`, the sum has mean `2T` and standard deviation `sT sqrt(2)`, so its CV is `s/sqrt(2)`.
3. **Make the beats dependent.** In `hsbh/synth.py` make each beat length correlated with the previous one (an AR(1) process with coefficient 0.7). Re-run `tests/test_cycle.py::test_quality_prefers_the_doubled_cycle...` logic. Does the doubled cycle still win? By how much?
4. **A better score.** The score ignores that a doubled cycle contains two S1-like events. Design a rule that uses this and test it with the simulation (use the true S1 times from `make_pcg` first, then estimated ones).
5. **Diastolic failure.** The half-cycle test false-alarms on diastolic murmurs. Plot the envelope of one such recording over one cycle and explain what makes `r(T/2)` high. Can you change the test so it works for them?
6. **Threshold.** Repeat the experiment with the threshold at 0.6, 0.8, 1.0. Plot hits against false alarms. Why is 0.8 not tuned, and why is that honest?
