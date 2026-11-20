# Worked — a password as the flag

1. hashdump → an NTLM hash for a user.
2. lsadump → a plaintext secret.
3. Or: ioc_scan the lsass process dump for a password string.
Either can be the flag or the next step's key.

## Notes

- lsadump yields plaintext for cached/logon secrets more often
  than hashdump, which returns NTLM hashes needing a crack.
- A cracked NTLM or a recovered secret is verbatim evidence — the
  plugin output is the quote.
