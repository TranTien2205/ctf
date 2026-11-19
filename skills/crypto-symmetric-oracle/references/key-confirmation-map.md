# Key confirmation and weak keys — map

| Surface | Signal | Attack |
|---|---|---|
| 'decrypt with key X' endpoint | ok/invalid | brute the key space |
| Handshake that confirms a shared key | success/fail | offline dictionary |
| Key = 4-byte PIN / 16-bit space | tiny | enumerate directly |
| Key derived from timestamp | ~seconds of space | seed-search |

Expanded rows and abort conditions: `key-confirmation.md` and `key-confirmation-deep.md`.
