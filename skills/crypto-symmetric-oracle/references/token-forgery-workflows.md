# Token forgery — from oracle to forged object

Most CTF oracle challenges end at a forged token: an admin cookie, a signed profile, a role=admin field. The path from oracle to forge is mechanical once the primitive is proven.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Token decrypts to a key=value profile | field-level forgery | ecb cut-and-paste or cbc bitflip |
| Token = mac(data) with raw MD hash | extension forgery | length-extension |
| Token = encrypted blob with known structure | splice or decrypt-and-re-encrypt | the applicable primitive |

## Steps

1. Identify the token's construction: ECB blocks, CBC+IV, or mac(data).
2. Run the matching primitive: cut-and-paste for ECB, bit-flip for CBC, length-extension for raw-MAC.
3. Forge the minimal change that reaches impact ('user'→'admin', 0→1, extra &role=admin).
4. Submit the forged token; the accepted privileged response is the evidence.
5. Record both the primitive AND the forgery in the evidence — the chain needs both to be reproducible.

## Falsifier

Falsifier — the token construction resists its intended primitive (authenticated, HMAC, sponge) and the forgery is rejected: re-run detection, the construction was misidentified.

## Traps

- A token that VALIDATES but doesn't grant the privilege means you forged the wrong field — map the privilege source first.
- Tokens often carry timestamps/expiry; the forgery must keep those fields valid.
- URL-encoding eats raw pad bytes — submit as hex or raw body where the endpoint accepts it.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
python3 tools/crypto_attack.py length-extension --hash sha1 --mac <m> --secret-len <n> --orig <o> --append '<a>'
```

## Cross-references

`ecb-cut-and-paste.md` · `cbc-bitflip.md` · `length-extension.md`
