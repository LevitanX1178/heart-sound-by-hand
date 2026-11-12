# Questions to be able to answer without the files

**Module 1.** Why does filtfilt not move the peaks? Why is its magnitude the square of one pass? What is the start-up state for, and what does odd padding do? Why can filtfilt not run in real time?

**Module 2.** What does the Hilbert transform add, and why is the amplitude `sqrt(x^2 + H^2)`? What does `p` do in the power mean? Where does `sigma = 0.1325 / fc x fs` come from? Why is the FIR Hilbert only an approximation?

**Module 3.** What does `r(l)` measure? Why is there a peak at `2T` as well as at `T`? Why is `r(T/2)` low for a real heartbeat? Why divide by the lag-0 sum?

**Module 4.** Why can a regularity-based score prefer a doubled cycle? Where does `1/sqrt(2)` come from, and when does it stop holding? What does the gate check, and what can it not check? When does the half-cycle test fail, and why does that matter for aortic regurgitation and mitral stenosis? What would you need to claim this works on patients?

**General.** What is the difference between a simulation result and a result on real recordings? Which numbers in this repository are tested, and against what?
