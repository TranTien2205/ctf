# Worked — the .pyc check — checklist

Companion to `the-worked-1.md`.

## Checklist

- [ ] 1. magic matches → marshal.loads(d[16:]).
- [ ] 2. --strings shows 'check_password' in co_names + suspicious consts.
- [ ] 3. dis the check function: XOR each byte with a key, COMPARE to a
- [ ] 4. Invert: answer = xor(stored, key). Run → accepted.
