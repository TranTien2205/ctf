# Evidence — what a proof looks like

## The class evidence

`crypto_attack.py` output — the recovered scalar `x`/`d`, the attack used,
the `--sigs`/`--order` inputs.

## The impact evidence

The verify: `x·G == Q` or `g^x mod p == h`, and the flag string `flag{…}`/
`CTF{…}` decrypted or revealed by the recovered key.

## The record shape

`post-probe` with:

- `hypothesis-id` — e.g. `ecdsa-nonce-reuse`
- `class` — `crypto-ecc-dlog`
- `evidence` — the verbatim tool output (the recovered scalar, the verify)
- `response` — the artifact bytes the evidence came from (the `sigs` file,
  the curve params)

## What is NOT evidence

- A plausible-looking scalar — the verify is mandatory.
- `bsgs`/`pohlig-hellman` partial output — only the final `x` that verifies.
- A flag-shaped `ct` never decoded — not a flag.

## The chain card components

After a real solve: `knowledge/chains/` card with the curve/params, the
attack id, the `--sigs` format, the falsifier that would have saved time,
the verify command. `tools/classify_solve.py` files it.
