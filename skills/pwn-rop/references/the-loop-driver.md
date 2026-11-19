# The driver loop — the full interaction


The complete driver: connect → recv prompt → send stage1 → recv
leak → compute → send stage2 → recv the observable → send the flag
read → the hook — each step bounded by a timeout.
