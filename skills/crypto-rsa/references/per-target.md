# Per-target map — what the challenge hands you → the attack

## A public key

`.pem`/`.der`/`.crt` → `n`,`e` only. The bug is in the *numbers*: `e` size,
`p`,`q` relation, or a leak from a *companion* artifact. The public key alone
is `n`,`e` — the attack needs the ciphertext or a leak.

## A ciphertext

`c` + `n`,`e` → the sheet. `e` small → `small-e`/`hastad`; `e` large →
`wiener`/`boneh-durfee`; a leak → `factor-from-d`/`crt`/`coppersmith`.

## A batch of keys/ciphertexts

`.json` of `n`,`e`,`c` → `batch-gcd` for a shared prime; `hastad` for the same
`m` under `e` coprime `n`.

## A private key

- **full** → `rsa-decrypt` — `n`,`e`,`d`,`p`,`q` held, `m=c^d`.
- **partial** → the field that isn't redacted: `p`-bits → `coppersmith`;
  `dp`,`dq`,`qInv` → `crt`; `d`/`phi` → `factor-from-d`.

## A generator script

`keygen.py`/`gen.py` → the *misuse* line: `next_prime` → fermat; `getPrime(d)`
→ wiener/boneh-durfee; `seed` → batch-gcd; `p-1` → pollard; `e=3` → small-e;
`m2=a·m1+b` → franklin-reiter.

## A signature service

correct + faulty `sig` of the same `m` → `crt` Bellcore.

## A socket / interactive

prints `n`,`e`,`c` → the numbers; computes on `m` → `crypto-symmetric-oracle`.

## A capture / artifact

`.pcap`, a `.bin`, a `.enc` → the `c`; the `n`,`e` from the handshake or the
companion key.

## The degenerate handout

`n=p²`, `n` prime, `n` multi-prime, `e`=1, `m`=0 — `phi` differs; the attack
adapts.
