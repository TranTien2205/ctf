# Detection index13 — the complete detection reference

## The detection family, the files

| File | Holds |
|---|---|
| `detection.md` | the signal vocabulary |
| `detection-deep.md` | the reads annotated |
| `detection-index*.md` | the indexes |
| `detection-catalogue*.md` | the keygen tells |
| `detection-matrix*.md` | observable × attack |
| `detection-map*.md` | the read-order |
| `detection-surface*.md` | the artifacts |
| `detection-playbook*.md` | the commands |
| `detection-checklist*.md` | the audit |
| `parameter-sheet*.md` | the sheet |
| `recon-order*.md` | the order |

## The reads, in order

1. The file types — `ls`/`file`/`xxd` → `.pem`/`.der`/`.json`/`.txt`/`.py`/`.bin`/`.pcap`.
2. `RSA.importKey` — `n`,`e`,`d`/`p`/`q`/`dp`/`dq`/`qInv`.
3. `re.findall` — the integers + counts.
4. `keygen`/`chal` grep — `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,no pad,
   `a·m1+b`,`dp`,`dq`,`qInv`,`redact`.
5. `crypto_attack.py list` — the ids + `lll_backend`.
6. The cheap reads — `n`,`e`,`c` counts; `e` size; `gcd(e,phi)`; `n` square/
   prime; `m^e` vs `n`.

## The output

The sheet: `n`,`e`,`c` counts; `e_sig`; the leak; the `keygen` tell; the
degenerate; `m^e` vs `n` — then `attack-table.md` → `per-bound.md` → the
attack → `pow`/`p*q` verify.

## The honest status

Catalogue — the detection produces the signal; the attack produces the proof.
