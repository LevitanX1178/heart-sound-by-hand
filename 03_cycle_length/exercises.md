# Module 3 exercises

1. **One lag by hand.** Take lag 2 on the first six envelope values only. Compute the deviations from their mean, the products at lag 2, and `r(2)`. Compare with a six-value version in a spare sheet.
2. **Why divide by the lag-0 sum?** What would the autocorrelation look like without it? Why does it make `r` comparable across recordings?
3. **Peak flag.** Read the formula in column J. Why is the condition `G > previous` and `G >= next` (one strict, one not)?
4. **Heart rate.** The allowed range in the project is 40 to 160 bpm. Convert to seconds and to lags at 50 samples per second. What lags does the search cover?
5. **Short recordings.** With only 4 seconds of signal, which lags have too few products to trust? Check how the number of products changes with the lag.
6. **Break it.** Change a few envelope values by hand (an artefact spike). What happens to the peaks?
