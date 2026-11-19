# small-e-root / nth-root — the wrap attack

`m^e<n` → `c` is a plain power → `m=c^{1/e}`. Detection: `e` small (3/5/17), `m`
short, no pad. Bound: `m^e<n` — `m^e≥n` → `hastad`/`coppersmith`. Verify:
`pow(m,e)==c`. Command: `crypto_attack.py small-e-root --c --e --n` /
`nth-root`. See `per-attack-small-e-root.md`.
