# Token forgery — from oracle to forged object — case catalogue

Most CTF oracle challenges end at a forged token: an admin cookie, a signed profile, a role=admin field. The path from oracle to forge is mechanical once the primitive is proven.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Token decrypts to a key=value profile | field-level forgery | ecb cut-and-paste or cbc bitflip |
| 2 | Token = mac(data) with raw MD hash | extension forgery | length-extension |
| 3 | Token = encrypted blob with known structure | splice or decrypt-and-re-encrypt | the applicable primitive |

## Falsifier

Falsifier — the token construction resists its intended primitive (authenticated, HMAC, sponge) and the forgery is rejected: re-run detection, the construction was misidentified.

## Coverage notes

- A token that VALIDATES but doesn't grant the privilege means you forged the wrong field — map the privilege source first.
- Tokens often carry timestamps/expiry; the forgery must keep those fields valid.
- URL-encoding eats raw pad bytes — submit as hex or raw body where the endpoint accepts it.

## Cross-references

`ecb-cut-and-paste.md` · `cbc-bitflip.md` · `length-extension.md`
