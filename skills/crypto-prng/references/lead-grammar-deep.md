# Lead grammar deep — the description cues, expanded

## The generator cues → route → confidence

| Cue | Route | Confidence |
|---|---|---|
| "LCG"/"linear congruential"/"`a·x+c`" | `lcg-*` | high |
| "LFSR"/"shift register"/"taps"/"GF(2)"/"polynomial" | `lfsr-*`/`berlekamp` | high |
| "mersenne"/"mt19937"/"`getrandbits`"/"`random`" | `mt19937-clone` | high |
| "xorshift"/"`x ^= x<<`"/"`x^=x>>`" | `xorshift128` | high |
| "seed"/"time-seeded"/"timestamp"/"`srand`"/"`mt_srand`" | seed-search | high |
| "rand()"/"mt_rand"/"java.util.Random"/"drand48" | the variant — fingerprint | medium |
| "random"/"predictable"/"nonce"/"ticket" | fingerprint — which? | medium |
| "secure"/"CSPRNG"/"`os.urandom`"/"`secrets`"/"`crypto`" | OUT | high |
| "AES"/"HMAC"/"keyed"/"cipher" | `crypto-symmetric-oracle` | high |

## The count cues → route

| Cue | Route |
|---|---|
| "three consecutive"/"a few outputs" | `lcg-recover` |
| "six or more"/"many outputs" | `lcg-unknown-modulus` |
| "leaks the high bits"/"top bits"/"`>>b`" | `lcg-truncated` |
| "keystream"/"bit stream"/"cipher" | `lfsr-*`/`berlekamp` |
| "624"/"a full window"/"every output" | `mt19937-clone` |
| "four consecutive"/"a handful" | `xorshift128` |
| "each call"/"per second"/"per request" | seed-search |

## The format cues → route

| Cue | Route |
|---|---|
| hex/base64/`0x` | decode |
| "float"/"decimal"/"`0.x`" | `×2^53`/variant |
| "`mod n`"/"`% N`" | the mod model |
| "`>> b`"/"high bits" | `lcg-truncated` |
| "`flag{`"/"`CTF{`" | the known-plaintext prefix |

## The trap cues → the warning

| Cue | Warning |
|---|---|
| "predict the next" — a game | the whole solve is prediction |
| "the flag is encrypted with a weak generator" | the keystream is the target |
| "java"/"php"/"javascript"/"c" | the platform variant — fingerprint |
