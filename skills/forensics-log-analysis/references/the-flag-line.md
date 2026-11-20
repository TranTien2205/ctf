# Hunting the flag line

    grep -inE 'flag|ctf|{.*}' access.log
    log_summary.py summary access.log   # flags flag-like lines

The flag may be a path, a param, a UA, or an embedded token —
grep widely.

## The patterns

- `flag{...}` / `CTF{...}` — the literal token.
- A base64/hex blob in a param or header.
- A path like `/the-flag-is/...` or `/s3cr3t/`.
- A username or password field containing it.
log_summary's summary pass already flags flag-like lines — check
its output first.
