# The one-shot write — when you get exactly one call


A one-shot service (no loop) gives exactly one format call: the whole
exploit — leak, plant, write, redirect — must fit one payload.

## Steps

1. Leak AND write in one call: %N$p specifiers read first, then the
   %Nc/%M$hn writes after.
2. The pointer must already be an arg (can't use a leaked addr to plant).
3. Target only deterministic addresses — non-PIE GOT, fixed hooks.
4. A win function needs no leak at all — pure write.

## Order in one call

    <reads %p %p ...><count padding><writes %N$hn><pointers at tail args>

## Falsifier

The write target needs a value only a leak could supply and the leak
arrives too late (same call): impossible in one shot — needs a loop.
