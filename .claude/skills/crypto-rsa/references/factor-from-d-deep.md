# factor-from-d deep — d/phi leak → the factors, the full treatment

## The mechanism

`d` (or `phi`) held → `ed - 1 = k·φ` is a multiple of `φ`. Write `ed-1 = 2^t·r`
(`r` odd); for random `g`, the sequence `g^r, g^{2r}, g^{4r}, ... mod n` reaches
a non-trivial `x` with `x² ≡ 1 mod n` → `gcd(x-1, n) = p`.

## Detection

- **`d`/`phi`/`dp`/`dq`/`qInv`/`p`/`q`** in the handout — a leak.
- **`phi` given** — `factor-from-d --n --phi` splits `n` directly.

## The bound / falsifier

The leaked `d`/`phi` must be real — `d`/`phi` fails `pow`/`p*q` → wrong input.

## The attack

```bash
python3 tools/crypto_attack.py factor-from-d --n <n> --e <e> --d <d>
python3 tools/crypto_attack.py factor-from-d --n <n> --e <e> --phi <phi>
# then rsa-decrypt --n --e --c --p --q with the recovered factors
```

## The chain

`d`/`phi` → `p`,`q` → `rsa-decrypt --n --e --c --p --q` → `m` → `pow` verify.

## The verify

`p*q==n` for the factors; `pow(m,e,n)==c` for the plaintext.

## The honest status

Standard — catalogue.
