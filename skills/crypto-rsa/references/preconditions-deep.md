# Preconditions deep — the conditions each attack needs

## The bound preconditions

- `fermat` — `|p-q|` small (`next_prime`/`p+k`/`p+2` keygen).
- `wiener` — `d < n^0.25` (large `e`).
- `boneh-durfee` — `d < n^0.292` (large `e`).
- `coppersmith-*` — a leak window `≥ n^0.25`/`n^(1/e)`.
- `small-e-root`/`nth-root` — `m^e < n`, no pad.
- `hastad` — `≥e` coprime `n`, same `m`, `∏n>m^e`, no pad.
- `common-modulus` — `gcd(e1,e2)=1`.
- `pollard-pm1` — `p-1` `B`-smooth.
- `batch-gcd` — a `gcd(ni,nj)>1` collision.
- `franklin-reiter` — `m2=a·m1+b` linear.
- `crt` — `∏pi>m` / `sig`+fault / `dp` consistent.
- `eth-root` — `gcd(e,phi)>1`, `p`,`q` held.
- `factor-from-d`/`rsa-decrypt` — `d`/`phi`/`p`,`q` held.

## The value preconditions

- The `n`,`e`,`c` integers parsed — real, not hex-garbage.
- The `d`/`phi`/`p`,`q`/`dp` held — the *right* value (`pow`/`p*q` verified).
- The `m^e`/`∏pi` product large enough for the wrap/CRT.

## The tool preconditions

- `crypto_attack.py list` — the id exists; `--help` for the flags.
- `lll_backend` — `fpylll` absent → pure-python LLL for `boneh-durfee`/`coppersmith`.
- `franklin-reiter` is `tools/crypto/franklin_reiter.py` — manual, not a
  `crypto_attack.py` id.
- `sympy`/`Crypto` for the manual `gcdex`/`factorint`/`crt`/`integer_nthroot`/
  `RSA.importKey`/`long_to_bytes`/`inverse`.

## The verify precondition

`pow`/`p*q` — the identity check must run; a candidate is not a flag.
