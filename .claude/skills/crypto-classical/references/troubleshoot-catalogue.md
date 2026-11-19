# Troubleshoot catalogue — the failure → the fix → the file

| Failure | The fix | File |
|---|---|---|
| `cipher_id` wrong family | `flag{` positions; layered → on output | `troubleshoot-deep.md` |
| `caesar` gives garbage | `subst`/`π`; strip non-letters | `troubleshoot-deep.md` |
| `vigenere` gives garbage | `L`/`L/2`/`2L`; `c=k-p`; autokey; `subst` | `troubleshoot-deep.md` |
| `subst` no language | `π`; `--restarts`/`--iters`; `flag{` anchor | `troubleshoot-deep.md` |
| `railfence` gives garbage | columnar `w`; route; `σ` | `troubleshoot-deep.md` |
| decode → another `ct` | `cipher_id` on output | `multi-step-chains.md` |
| `flag{` reads `synt{` | decode the format (ROT13) | `caesar-deep.md` |
| `+/=`/hex `ct` | `enc_detect` — not a cipher | `detection.md` |
| `gLAG{...}` | the `flag{` positions pin `σ` | `subst-deep.md` |
| a name not in the tool | `other-ciphers.md` → a script | `other-ciphers.md` |
