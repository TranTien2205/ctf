# Many args in one call — the deep-scan fmtstr


A single format string can carry dozens of specifiers: `%p.%p.%p...` for
50 positions dumps 50 words in one call — the whole stack region mapped.

## Steps

1. Send a long %p run — 30-60 specifiers.
2. Parse the reflected words in order.
3. Map: your input at N, canary at N+k, return addrs deeper.

## Falsifier

Output truncation cuts the run short — send in two calls, or accept the
partial map.
