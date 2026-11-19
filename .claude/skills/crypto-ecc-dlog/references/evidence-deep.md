# Evidence deep — the proof stack in full

## What counts

- The verbatim `crypto_attack.py` output — the recovered `x`/`d`.
- The verbatim verify transcript — `x·G == Q` or `g^x == h` returning true.
- The verbatim decoded bytes containing `flag{…}`/`CTF{…}`.
- The `--sigs` file contents and the `--order`/`--nonce-*`/`--bound` values
  that produced the result.

## What does NOT count

- A plausible `d` that never passed `x·G == Q`.
- A lattice candidate list — only the verifying scalar.
- A `flag{`-shaped string never decoded from the recovered key.
- `bsgs`/`pohlig-hellman` partial progress (no collision ≠ a result).

## The post-probe shape

```
tools/hooks.py post-probe \
  --challenge <name> \
  --hypothesis-id ecdsa-nonce-reuse \
  --class crypto-ecc-dlog \
  --evidence-kind class \
  --evidence "ecdsa-nonce-reuse: d=0x..., d·G == Q verified" \
  --response "<verbatim tool output>"
```

`evidence` must be a substring of `response` — the gate checks it.

## The chain-card shape

A solved `crypto-ecc-dlog` challenge produces a `knowledge/chains/` card with:
the params, the attack id, the exact command, the falsifier that would have
saved time, the verify transcript. `classify_solve.py` files it.

## The negative evidence

A falsifier (`no dup r`, `smoothness` large factor, `d·G ≠ Q`) is recorded
the same way — `negative-results*.md`.
