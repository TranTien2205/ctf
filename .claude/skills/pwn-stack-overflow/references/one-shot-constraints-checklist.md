# One-shot constraints — no re-trigger — checklist

The service runs once: no leak-then-exploit. The whole attack must fit a single input — or the leak must be embedded.

## Checklist

- [ ] If the service is one-shot, the leak and the exploit must compose in one input, OR a non-leak chain is needed.
- [ ] Options: hardcode an offset that brute-forces the low-byte (if only partial ASLR), use an unprivileged read that leaks inside the same run, or design a leak-free chain.
- [ ] A return-to-a-print-function inside the smash can leak AND continue the chain (print something, then continue).

## Abort conditions

- A leak-free chain exists when ASLR leaves some bytes predictable, or when the target is non-PIE + no-leak-needed.
- The same-input composition: leak via a format read inside the smash, then use it.
- The least-squares answer: brute-force the one unknown byte across many runs.

## Falsifier

Falsifier — the chain genuinely needs two stages and the service is one-shot: find a leak-free alternative or a different bug.
