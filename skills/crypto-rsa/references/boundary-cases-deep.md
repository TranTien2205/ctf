# Boundary cases deep — the bound at its edge

## `d` exactly `n^0.25`

Wiener's boundary — the CF may or may not carry `d` in a convergent at the edge.
If `wiener` returns nothing at `d≈n^0.25`, escalate to `boneh-durfee` — it
reaches `n^0.292`, a strictly wider bound.

## `d` exactly `n^0.292`

Boneh-Durfee's bound — the LLL approximation factor. At the edge the lattice
`m`,`t` must grow; `boneh-durfee-escalate` raises them. `d>n^0.292` is a
theorem — record the negative.

## The Coppersmith `n^0.25` edge

`p` unknown window exactly `n^0.25` — the `β=½` bound. The pure-python LLL may
be weaker at the edge than `fpylll`; the bound is the same, but the *practical*
recovery may fail where `fpylll` succeeds. Measure the window — `< n^0.25` is
closed, `≥` is the working region.

## `e` = `n` exactly

`e = inverse(d, phi)` for `d`=1? No — `e≈n` means small `d`, the wiener/boneh
territory. `e` = `n` literally would mean `d·e≡1 mod phi` with `e`≈`phi` → `d`
≈ 1 — a degenerate `d`, `m=c` mostly.

## `m` exactly `n^(1/e)`

The wrap boundary — `m^e` just under `n` → `small-e-root`/`hastad` recover `m`;
just over → the wrap happened, root fails. Measure `m.bit_length()*e` vs
`n.bit_length()`.

## `hastad` with exactly `e` recipients

`∏ni` vs `m^e` — the CRT product must exceed `m^e` for the root to be `m`, not
`m mod ∏ni`. Exactly `e` *distinct* coprime `n` is the minimum; `e-1` fails.

## `common-modulus` `gcd(e1,e2)=1` edge

`gcd=1` required. `gcd=e1` (e1|e2) → `m^e1`, not `m` — then `nth-root` if
`m^e1<n`. `gcd>1` generally → `m^gcd`.

## `fermat` `|p-q|` edge

`|p-q|` small → `a` climbs fast. `|p-q|` large → `a` walks `O(|p-q|)` —
impractical. The `a`-budget is the falsifier.

## `pollard-pm1` `B` edge

`B` ≥ the largest `p-1` factor — exactly at the boundary the `gcd` fires. Raise
`B` to cover the edge; `p-1` not `B`-smooth is the negative.

## `crt` `∏pi` edge

`∏pi > m` required for a unique `m`. `∏pi = m` — `m` is recoverable exactly.
`∏pi < m` — `m mod ∏pi` only.

## `eth-root` `gcd(e,phi)` edge

`gcd(e,phi)=g` — `g` candidate roots. `g` large → many candidates; `pow`+format
still picks. `g=1` → a normal `inverse`, not `eth-root`.
