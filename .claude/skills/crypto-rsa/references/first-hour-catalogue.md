# First-hour catalogue — the hour, the reads, the output

## The reads, in order

- `crypto_attack.py list` — the inventory + `lll_backend`.
- `parameter-sheet.md` — `n`,`e`,`c`,counts,`e_sig`,leak,keygen,degenerate.
- `RSA.importKey` — `n` bits, `e`, private fields.
- `re.findall(r'\d{20,}')` — the integers.
- `grep -E "getPrime|next_prime|seed|e ?=|inverse|p-1|m2|dp|dq|qInv|print|redact"` — the tells.
- The counts/`e` size/`gcd`/square/`m^e` — the discriminating reads.
- `attack-table.md` → `per-bound.md` → `crypto_attack.py <id>` → `pow`/`p*q`.

## The output

A signal, a bound, an attack — and the sheet. Not a flag yet — the flag is
`pow(m,e,n)==c` + the bytes.

## The budget

`decide.py` — 5 probes / 15 active min per class, 25/45 per challenge.
