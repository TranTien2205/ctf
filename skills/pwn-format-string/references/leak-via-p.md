# Leak via %p/%x — reading the stack

A run of %p specifiers dumps consecutive stack words: pointers, the canary, return addresses — the leak primitive that feeds every downstream chain.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| %p in a reflected output | stack dump | read the words |
| a canary-shaped word at a known depth | canary leaked | preserve it |
| a code/libc pointer shape | base leaked | compute the base |

## Steps

1. Send %p.%p.%p.… — read the run of leaked words.
2. Identify the canary (a word ending in 00 usually) at its depth.
3. Identify a code or libc pointer for the PIE/libc base.
4. Use %N$p to read a specific depth once the offset is known.

## Falsifier

Falsifier — the output truncates the %p run or only some args are reachable: the needed depth isn't readable.

## Traps

- A %p leak is data-dependent — the canary's depth varies by call depth.
- PIE base needs a code pointer; libc base needs a libc pointer — different leaks.
- The canary ends in 00 (little-endian) — the signature is the 00 byte.

## Cross-references

`format-string-leak.md` · `canary-pie-composition.md`
