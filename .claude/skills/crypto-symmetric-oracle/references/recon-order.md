# Recon order — first 30 minutes on an oracle challenge

## 0-5 min: shape the handout

- `python3 tools/crypto_attack.py list` — name what's available.
- Source? grep for: `encrypt`, `decrypt`, `iv`, `nonce`, `key`, `mac`,
  `pad`, `mode`. The mode name usually sits next to the cipher.
- No source? The endpoint's response shape answers the same questions.

## 5-10 min: determinism + length

- Same input twice: deterministic?
- Grow input: block-step or 1:1?

## 10-15 min: the oracle kind

- 'A'*48: ECB fingerprint?
- Corrupt mid-CT: pad-vs-MAC distinguishable?
- Tag verified before decrypt? → boundary check.

## 15-25 min: pick the attack

Match `detection.md`'s table → the attack file → the tool. Run the tool's
`--selftest` once if it exists (proves the driver before spending target
requests).

## 25-30 min: first confirming probe

- ECB: the duplicate-block observation → post-probe class evidence.
- Padding oracle: the two-corruption split → post-probe class evidence.
- Nonce reuse: the two captured records → post-probe class evidence.

## After 30 min without a named oracle

Record what was ruled out (determinism? length profile? distinguishability?)
in field-notes. Reclassify or escalate — do not keep probing blind.
