# Detection index5 — the detection family, the summary

## The phase

The detection phase fills `parameter-sheet.md` from the artifacts — the reads
produce the signal, the signal names the attack, the bound falsifies it.

## The reads, in order

1. The file types — `ls`/`file`/`xxd` → `.pem`/`.der`/`.json`/`.txt`/`.py`/`.bin`/`.pcap`.
2. `RSA.importKey` — `n`,`e`,`d`/`p`/`q`/`dp`/`dq`/`qInv`.
3. `re.findall(r'(?:0x)?[0-9a-fA-F]{20,}|\b\d{20,}\b')` — the integers + counts.
4. `keygen`/`chal`/`gen` grep — `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,
   no pad,`a·m1+b`,`dp`,`dq`,`qInv`,`redact`.
5. `crypto_attack.py list` — the ids + `lll_backend`.
6. The cheap reads — `n`,`e`,`c` counts; `e` size; `gcd(e,phi)`; `n` square/
   prime; `m^e` vs `n`.

## The output

The sheet: `n`,`e`,`c` counts; `e_sig`; the leak; the `keygen` tell; the
degenerate; `m^e` vs `n`. → `attack-table.md` → `per-bound.md` → the attack.

## The files

`detection*.md`,`parameter-sheet*.md`,`recon-order*.md`,`detection-catalogue*`,
`detection-matrix*`,`detection-map*`,`detection-surface*`,`detection-playbook*`,
`detection-checklist*`.
