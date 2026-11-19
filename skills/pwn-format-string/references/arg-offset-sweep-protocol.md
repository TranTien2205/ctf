# The arg-offset sweep — the precise protocol


The definitive sweep: send 'AAAABBBB' followed by %N$p for each N until
your marker appears — records the arg index AND its alignment.

## Steps

1. Send 'AAAABBBB' + '.%N$p' for N=1..~30.
2. The N printing 0x4242424241414141 (or the aligned variant) is your arg
   index.
3. If the marker straddles a boundary, you'll see it at N and N+1 — pick
   the aligned one.
4. Record N — all %N$ ops use it.

## Falsifier

The marker never appears at any N: your input isn't a printf argument in
this call — re-check the format position.
