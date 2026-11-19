# fermat — the close-prime factorisation

`|p-q|` small → `n=a²-b²`, `a` near `√n`. Detection: `next_prime`/`p+k`/`q=p+2`/
a shared seed in the keygen. Bound: `|p-q|` small — the `a` walk is `O(|p-q|)`.
Chain: `p`,`q`→`phi`→`d`→`m`→`pow`. Command: `crypto_attack.py fermat --n <n>`.
See `per-attack-fermat.md` for the full module.
