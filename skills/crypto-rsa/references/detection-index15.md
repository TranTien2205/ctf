# Detection index15 — the detection family, final index

## The files

The `detection*` family — the signal vocabulary (`detection*.md`), the indexes
(`detection-index*.md`), the keygen tells (`detection-catalogue*`), the
cross-table (`detection-matrix*`), the read-order (`detection-map*`), the
artifacts (`detection-surface*`), the commands (`detection-playbook*`), the
audit (`detection-checklist*`), the sheet (`parameter-sheet*`), the order
(`recon-order*`).

## The procedure

1. The file types — `ls`/`file`/`xxd`.
2. `RSA.importKey` — `n`,`e`,`d`/`p`/`q`/`dp`/`dq`/`qInv`.
3. `re.findall` — the `n`,`e`,`c` integers + counts.
4. `keygen`/`chal` grep — the tell.
5. `crypto_attack.py list` — the ids + `lll_backend`.
6. The cheap reads — counts, `e` size, `gcd`, square, `m^e`.

## The route

`attack-table*.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify*`.

## The verify

`pow(m,e,n)==c` / `p*q==n` — the deterministic gate.

## The honest status

Catalogue — detection produces the signal; the attack produces the proof.
