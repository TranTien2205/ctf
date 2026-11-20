# Question — the flag line

    grep -inE 'flag|ctf|\{[A-Za-z0-9_]+\}' access.log

Or the path/UA/param field — the flag token hides in any field;
grep widely across formats.

## The sweep

- grep the literal token patterns.
- Check the one-off path tail for a /flag or /secret.
- Check UAs and usernames for embedded tokens.
- Try base64/hex patterns in params.
log_summary's summary flags flag-like lines automatically.
