# Evidence â€” what proves each stage — deep

Companion to `evidence.md`.

## Why it matters

Stack-corruption work is measurement work: the protection report decides the chain, the cyclic offset is empirical, and every falsifier is a cheap probe that closes a whole branch. The aggregator module is the discipline that keeps an agent from re-walking dead routes; this companion holds the reasoning behind it.

## Invariants

- The offset is measured by cyclic+fault, never assumed.
- Each falsifier is checked before the chain is built, not after it fails.
- A crash is not control; control is a faulting RIP holding pattern bytes.
- Evidence quotes the actual response/register dump.
