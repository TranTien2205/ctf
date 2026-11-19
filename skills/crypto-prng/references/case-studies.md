# Case studies — the narrated shapes

## The LCG token service

A service issues session tokens `t_{i+1} = a·t_i + c mod m`. Collect three,
`lcg-recover --modulus m` → `a`,`c` → predict the admin's next token →
authenticated endpoint → `flag{`.

## The unknown-modulus LCG

`rand()` on a custom CRT/glibc — six consecutive outputs →
`lcg-unknown-modulus` → `m` → `lcg-recover` → `a`,`c` → predict.

## The truncated LCG keygen

A keygen leaks `key >> 32` per call — `m`,`a`,`c` from source →
`lcg-truncated --low-bits 32` → the state → the key.

## The LFSR stream cipher

A `ct = m ⊕ lfsr_keystream` — BM on the keystream → `(width, taps)` →
`lfsr-recover` → `lfsr-predict` → keystream → `ct ⊕ ks` → `flag{`.

## The MT session id

`session_id = str(random.getrandbits(32))` — collect 624 → `mt19937-clone`
→ `predict_next` → the admin's id → session hijack → flag.

## The timestamp seed

`token = sha256(str(time()))` or `random.seed(int(time()))` — bound the
epoch to the issuance window → enumerate → match → predict.

## The xorshift cookie

4 cookie values → `xorshift128 --outs` → `--predict` → next cookie → flag.

## The pattern

Every case is: identify generator → count outputs → the matching attack →
verify on a held-back output → use → flag.
