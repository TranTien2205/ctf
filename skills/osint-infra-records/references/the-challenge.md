# The CTF shape — planted records

CTF DNS challenges plant the flag in a TXT, a custom type, or a
SAN-named host — the record is the answer, not a step. Read it
verbatim; don't overthink a planted string.

## The shapes

- `flag{...}` in a TXT record.
- A flag-named subdomain (`flag.example.com`).
- A SAN that names the flag host.
- An encoded value (base64) inside a TXT.
The record itself is the measurement — quote it.

## Verbatim

A planted record is read verbatim — the answer is the string, not an interpretation of it.
