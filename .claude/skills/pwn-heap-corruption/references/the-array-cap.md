# The slot cap — the op budget's ceiling


The pointer array's size caps live objects — 10, 20, 64 slots: the cap
bounds spray and grooming depth.

## The math

7 frees for tcache-drain + guards + the victim + the fakes — count the
slots the technique needs vs the cap.

## Falsifier

The cap can't express the sequence: compress it (smaller guards,
fewer drains) or pick a cheaper technique.
