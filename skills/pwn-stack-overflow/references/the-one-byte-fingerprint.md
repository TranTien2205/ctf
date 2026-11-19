# The one-byte fingerprint — inferring a canary/addr from one byte


A byte-at-a-time oracle (crash-or-clean) reveals a value one byte at a
time — the fork-server canary brute is the canonical example, but it
generalizes to any byte-revealing oracle.

## Shapes

- Canary byte brute: crash = wrong, clean = right.
- A 1-byte partial-write redirect's feasibility.
- An uninitialized-read that reveals one byte at a controlled offset.

## The rule

Each byte's brute is ≤256 tries; 8 bytes is ≤2048 — feasible when the
oracle is stable across attempts.
