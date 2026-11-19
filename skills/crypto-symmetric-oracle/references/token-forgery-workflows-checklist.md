# Token forgery — from oracle to forged object — operational checklist

Most CTF oracle challenges end at a forged token: an admin cookie, a signed profile, a role=admin field. The path from oracle to forge is mechanical once the primitive is proven.

## Checklist

- [ ] Identify the token's construction: ECB blocks, CBC+IV, or mac(data).
- [ ] Run the matching primitive: cut-and-paste for ECB, bit-flip for CBC, length-extension for raw-MAC.
- [ ] Forge the minimal change that reaches impact ('user'→'admin', 0→1, extra &role=admin).
- [ ] Submit the forged token; the accepted privileged response is the evidence.
- [ ] Record both the primitive AND the forgery in the evidence — the chain needs both to be reproducible.

## Abort conditions

- A token that VALIDATES but doesn't grant the privilege means you forged the wrong field — map the privilege source first.
- Tokens often carry timestamps/expiry; the forgery must keep those fields valid.
- URL-encoding eats raw pad bytes — submit as hex or raw body where the endpoint accepts it.

## Falsifier

Falsifier — the token construction resists its intended primitive (authenticated, HMAC, sponge) and the forgery is rejected: re-run detection, the construction was misidentified.

## Cross-references

`ecb-cut-and-paste.md` · `cbc-bitflip.md` · `length-extension.md`
