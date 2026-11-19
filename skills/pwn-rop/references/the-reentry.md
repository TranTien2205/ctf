# The re-entry — returning to main


Stage 1's last entry returns to the vulnerable path — main or the
read loop — the program runs again, and stage 2 fires on the next
input.

## The requirement

The re-entry target must re-reach the overwrite — verify the code
path loops back, or the exploit needs a restartable process model.

## Falsifier

No re-entry: single-stage — the leak and the chain must coexist in
one run, or a persistent service must be assumed.
