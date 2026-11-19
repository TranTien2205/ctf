# Common mistakes variant — the traps restated by family

## Nonce mistakes

- **"similar `r` is reuse"** — identical bytes only; close `r` is the biased case.
- **"`s` repeats mean reuse"** — `s` values collide freely; only `r` detects `k` reuse.
- **"one sig is enough"** — one sample carries zero nonce info.
- **"`z` is the message"** — `z` is `int(H(m))` truncated to `order_bits`.
- **"`--nonce-bits` is the bound"** — it's `k < 2^B`; `--nonce-bound` is the integer `B`.

## Dlog mistakes

- **`--order = p`** — it's `n`/`ord(g)`, never `p`.
- **skipping `smoothness`** — `bsgs` on a 200-bit `ord` stalls forever.
- **PH on `p-1 = 2q`** — safe-prime kills it; the bug is elsewhere.
- **`h` outside `<g>`** — `pow(h, ord, p) == 1` first.
- **curve `bsgs` via `dlog.bsgs`** — `dlog` is for `Fp*`; use `ec.py` ops.

## Curve mistakes

- **`Δ ≈ 0` counts as singular** — must be `≡ 0 mod p` exactly.
- **`#E ≈ p` counts as anomalous** — must equal `p` exactly.
- **`secp256k1` defect-hunting** — a real curve has no defect; the bug is the nonce.
- **feeding `n` where `p` belongs in `ec.curve`** — `{"p","a","b"}` are the params.

## Evidence mistakes

- A `d` recorded before `d·G == Q` — a candidate, not a key.
- `crypto_attack.py` output treated as final — verify first.
- A `flag{` substring never produced by the recovered scalar.
