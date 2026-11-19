# Detection index11 — the last detection index

## The reads, final

- The file types — `ls`/`file`/`xxd`.
- `RSA.importKey` — `n`,`e`,private fields.
- `re.findall` — the integers + counts.
- `keygen`/`chal` grep — the tells.
- `crypto_attack.py list` — the inventory.
- The counts/`e`/`gcd`/square/`m^e` — the discriminating reads.

## The signals → the attacks

`e` small → `small-e`/`hastad`/`franklin-reiter` · `e`≈`n` → `wiener`/
`boneh-durfee` · `gcd(e,phi)>1` → `eth-root` · `n`s share `p` → `batch-gcd` ·
`p-1` smooth → `pollard-pm1` · `p`/`m` bits → `coppersmith` · `a·m1+b` →
`franklin-reiter` · `sig` fault/`dp`/`m` residues → `crt` · `d`/`phi`/`p`,`q` →
`factor-from-d`/`rsa-decrypt` · `|p-q|` small → `fermat` · `n`=p²/prime →
degenerate.

## The route

`attack-table*.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify*`.

## The files

`detection*.md`,`parameter-sheet*.md`,`recon-order*.md` — the family.
