# Lead grammar — the description cues → the route

## The generator cues

| Cue phrase | Route |
|---|---|
| "random"/"predictable"/"nonce"/"ticket" | fingerprint — which generator? |
| "LCG"/"linear congruential"/"`a·x+c`" | `lcg-*` |
| "LFSR"/"shift register"/"taps"/"GF(2)" | `lfsr-*` |
| "mersenne"/"mt19937"/"random.getrandbits" | `mt19937-clone` |
| "xorshift"/"`x ^= x<<`" | `xorshift128` |
| "seed"/"time"/"timestamp-seeded" | seed-search |
| "rand()"/"srand"/"mt_rand"/"java.util.Random" | the variant — fingerprint |

## The count cues

| Cue | Route |
|---|---|
| "three consecutive" | `lcg-recover` |
| "six or more" | `lcg-unknown-modulus` |
| "leaks the high bits" | `lcg-truncated` |
| "keystream"/"bit stream" | `lfsr-*`/`berlekamp-massey` |
| "624"/"many outputs" | `mt19937-clone` |
| "four consecutive" | `xorshift128` |

## The trap cues

| Cue | Route |
|---|---|
| "secure"/"CSPRNG"/"os.urandom"/"secrets" | NOT this class |
| "AES"/"CBC"/"XOR-keyed" | `crypto-symmetric-oracle` |
| "hash"/"HMAC"/"SHA" | different class |
| "RSA"/"modulus pq" | `crypto-rsa` |

## The format cues

| Cue | Route |
|---|---|
| hex/base64 | decode |
| floats | ×2**53 pair |
| `mod n`/`>> b` | truncated/reduced |
| timestamp-like | seed-search |
