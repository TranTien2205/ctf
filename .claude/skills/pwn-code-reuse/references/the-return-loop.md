# The return loop — a chain that re-enters


A chain ending at the vuln function re-runs the program — the same
exploit re-fires with updated knowledge; the loop IS the multi-stage
delivery.

## The pattern

    stage1 = leak + ret-to-vuln
    stage2 = the real chain

## Falsifier

The re-entry path resets state you needed (fresh stack canary you
can't re-leak): single-stage.
