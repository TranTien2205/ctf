# The miss — when a gadget doesn't do its job


A gadget that doesn't set the register: the tail had a side effect
that clobbered it, or the pop consumed a different slot than planned.

## The diagnosis

Step the gadget in r2 -d: watch the register before and after — the
discrepancy names the cause.
