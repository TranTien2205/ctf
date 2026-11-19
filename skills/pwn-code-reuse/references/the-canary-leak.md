# Leaking the canary — the prerequisite


A canary blocks the overwrite — leak it first:

- A format-string read of the canary's slot.
- An info-disclosure bug reading stack data.
- Brute-force on a fork-server (the canary is per-process, constant
  across connections on some setups — byte-by-byte oracle).

## Falsifier

No leak channel and a per-connection re-randomized canary: the
overwrite is blocked — a different bug-class entry is needed.
