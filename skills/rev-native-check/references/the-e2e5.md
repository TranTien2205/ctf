# End to end — the early-exit oracle


A byte-check that exits on the first wrong byte:

1. For position i: try bytes until the response deepens (a longer
   run, a different exit).
2. The confirmed byte extends the known prefix.
3. n positions × the tries = the answer.
