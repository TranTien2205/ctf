# Boundary map — the boundary → the files

## The count boundaries → files

| Boundary | Files |
|---|---|
| `lcg-*` floors (3/6/req) | `boundary-*`,`per-attack-lcg-*`,`per-boundary` |
| `lfsr-*` floor (2w) | `boundary-*`,`per-attack-lfsr-*`,`per-attack-berlekamp*` |
| `mt19937` floor (624) | `boundary-*`,`per-attack-mt19937-*` |
| `xorshift` floor (4) | `boundary-*`,`per-attack-xorshift*` |
| seed window | `boundary-*`,`per-family-seed*` |

## The convention boundaries → files

| Boundary | Files |
|---|---|
| `--low-bits` dropped | `common-*`,`per-attack-lcg-truncated*` |
| `--taps` indexing | `per-attack-lfsr-*`,`per-family-lfsr*` |
| `--outputs` order | `payload-*`,`common-*` |
| MT word = `getrandbits(32)` | `per-attack-mt19937-*` |

## The shape boundaries → files

| Boundary | Files |
|---|---|
| `x>>b` vs `x mod n` | `edge-*`,`boundary-*` |
| raw vs float/`randint` | `edge-*`,`operator-notes*` |
| bits vs words | `cipher-id*`,`detection*` |

## The seed boundaries → files

| Boundary | Files |
|---|---|
| bounded window | `per-family-seed*`,`boundary-*` |
| unbounded/`urandom` | `class-boundary*` |

## The class boundaries → files

| Boundary | Files |
|---|---|
| CSPRNG/keyed | `class-boundary*` |
| encoding-carrier | `class-boundary*` |
| ecc/rsa nonce | `class-boundary*` |
