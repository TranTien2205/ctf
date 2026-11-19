# The verification — beyond running it once

## Single-input verify

`./chal 'produced'` → WIN — necessary but minimal.

## The stronger verify

- Run it twice — deterministic.
- The flag through hooks.py pre-flag with the WIN output as evidence.
- The decoded program + the accepted input both recorded.

## The non-verifiable

If the binary won't run, replicate the VM in Python — the inverted
input verified against YOUR OWN VM implementation of the recovered
table is the fallback, but weaker than the real binary.
