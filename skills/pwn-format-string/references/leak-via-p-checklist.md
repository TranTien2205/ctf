# Leak via %p/%x — reading the stack — checklist

A run of %p specifiers dumps consecutive stack words: pointers, the canary, return addresses — the leak primitive that feeds every downstream chain.

## Checklist

- [ ] Send %p.%p.%p.… — read the run of leaked words.
- [ ] Identify the canary (a word ending in 00 usually) at its depth.
- [ ] Identify a code or libc pointer for the PIE/libc base.
- [ ] Use %N$p to read a specific depth once the offset is known.

## Abort conditions

- A %p leak is data-dependent — the canary's depth varies by call depth.
- PIE base needs a code pointer; libc base needs a libc pointer — different leaks.
- The canary ends in 00 (little-endian) — the signature is the 00 byte.

## Falsifier

Falsifier — the output truncates the %p run or only some args are reachable: the needed depth isn't readable.
