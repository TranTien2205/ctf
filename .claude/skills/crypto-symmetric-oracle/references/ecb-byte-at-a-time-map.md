# Byte-at-a-time ECB decryption — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| You control a prefix position before a hidden secret in the same plaintext | byte-at-a-time applies | alignment then the guess loop |
| Appended secret length measurable by growing input | secret length recoverable | boundary measurement |
| Random prefix before your input | alignment breaks | find the fixed suffix or give up ECB |

## Falsifier

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).
