# Onboarding — crypto-rsa in five minutes

## What this class is

A challenge hands you RSA **numbers** — `n`, `e`, `c`, maybe a leak — and asks
for the plaintext or a private value. The bug is never in RSA — it's a violated
factoring precondition.

## The one procedure

```
parameter-sheet → discriminator → bound-check → attack → pow-verify → record
```

## The commands

```bash
python3 tools/crypto_attack.py list          # the attacks + bounds
python3 tools/crypto_attack.py <id> --help   # the flags
python3 tools/crypto_attack.py <id> <flags>  # run it
```

## The six bug families

wrap (small-e/hastad) · gap (fermat) · divisor (batch-gcd/pollard) · exponent
(wiener/boneh-durfee/common-modulus/factor-from-d) · partial (coppersmith) ·
relation/leak (franklin-reiter/crt/eth-root/rsa-decrypt).

## The verify

`pow(m,e,n)==c` or `p*q==n` — the only proof.

## The honest status

Catalogue — no local solve. The bounds are the falsifiers; `../field-notes.md`
records real solves.

## Where next

`attack-table.md` — the discriminator; `decision-table.md` — the one-look router;
`../SKILL.md` — the routing table; `README.md` — the index.
