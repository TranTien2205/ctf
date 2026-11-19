# Theory notes — the working facts

## The one fact that matters

RSA = `m^e mod n` with `ed ≡ 1 mod φ`. Breakable when a *precondition* of
factoring fails. Every attack is one of six precondition violations.

## The six violations

1. **Wrap** — `m^e<n` → exact root. `small-e-root`, `hastad`.
2. **Gap** — `|p-q|` small → `n=a²-b²`. `fermat`.
3. **Divisor** — shared `p`, or smooth `p-1` → `gcd`. `batch-gcd`, `pollard-pm1`.
4. **Exponent** — `d` small or `e` shared → `ed≡1 mod φ` leaks. `wiener`,
   `boneh-durfee`, `common-modulus`.
5. **Partial** — bits of `p`/`m` known → Coppersmith small-root. `coppersmith`.
6. **Leak** — `d`/`φ`/`dp`/`p`,`q` held → arithmetic. `factor-from-d`, `crt`.

## The two bounds to memorize

- `d < n^0.25` (Wiener), `d < n^0.292` (Boneh-Durfee) — the small-`d` window.
- unknown `< n^0.25` (Coppersmith `β=½`) — the partial-`p` window.

## The verify

`pow(m,e,n)==c` or `p*q==n`. The only proof.

## The non-obvious facts

- A large `e` *is* the small-`d` tell — `e=inverse(d,φ)` for small `d` ≈ `n`.
- `e=3` is weak only when `m³<n` — a real flag usually wraps.
- `m2=a·m1+b` breaks the padding-safety — `franklin-reiter` exploits the relation.
- `n=p²`/`n` prime are degenerate — `φ=p(p-1)` or `n-1`.
- `gcd(e,φ)>1` → `eth-root`, not a failed `inverse`.
- A shared `q` splits identically to a shared `p` — `gcd` doesn't care.
