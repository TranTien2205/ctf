# Class boundary - what a race is not

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

A race needs a check-then-act or read-modify-write pair where the
order between two requests decides the outcome. It is NOT: a replay
attack with no overlap (the serial baseline would show the same
signature), an idor that fails closed (the second request is simply
unauthorized), or a double-spend that needs no concurrency (a logic
flaw). The discipline: serial baseline FIRST, then overlap proof,
then N-of-M counts - skip any and the claim is unmeasurable.

## Evidence chain

1. Serial run: the outcome does not occur -> the signature is
   concurrency-dependent.
2. Overlap run: the tool's timing shows the requests actually
   overlapped - no overlap, no claim.
3. Count: K successes in N overlapped attempts, with K > serial
   baseline success count.

## Pivot

Boundary applies -> logic-flaw (invariant broken without timing) or
replay questions (race-condition sibling classes).
