# The win function — finding it


A flag-printing / shell-giving function in the binary is the shortest
target — find it:

    r2 -A ./chal ; afl | grep -iE 'win|flag|shell|getflag'
    strings ./chal | grep -iE 'flag\{|/bin/sh'

## The call

A single ret to it — args usually unneeded.

## Falsifier

No win function: a real call is required.
