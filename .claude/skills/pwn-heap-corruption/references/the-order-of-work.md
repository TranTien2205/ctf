# The order of work — the exploit's outline


1. version → 2. primitive → 3. map ops → 4. leak → 5. groom →
6. corrupt → 7. verify → 8. write → 9. fire → 10. flag.

Each stage's falsifier is the next stage's precondition — check before
proceeding, not after failing.
