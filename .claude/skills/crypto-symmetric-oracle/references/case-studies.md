# Case studies — shaped walks through the standard surfaces

Not solved-here claims — these are the canonical shapes the class was built
against, with the decision path each takes.

## 1. Encrypted profile cookie (ECB cut-and-paste)

A service issues `AES-ECB(user=<email>&role=user&uid=42)` as a cookie.
- Detection: same email prefix → same leading blocks.
- Attack: mint `email=AAAA...&role=admin<padding>` so the last block is
  'role=admin'+pad; splice that block over the real token's role block.
- Evidence: the forged cookie returns an admin page.
- Falsifier that would have closed it: a MAC in the cookie.

## 2. Captcha/ticket service (byte-at-a-time)

`encrypt(attacker_input || secret_flag)` under ECB.
- Detection: 'A'*47 repeated produces two identical blocks.
- Loop: ecb_oracle.py recovers the flag one byte per 256 requests.
- Request cost: ~len(flag) × 256; at 10 req/s a 32-byte flag is ~14 min.

## 3. The CBC token that errors differently (padding oracle)

Service returns 403 on bad pad, 200-then-MAC-fail on good pad.
- Two distinguishable answers — the oracle exists.
- pad_oracle.py --ok-regex 'bad mac' decrypts the token.
- False-positive handling at \\x01 pads is where hand-rolled loops break.

## 4. The reused-nonce log (crib-drag)

Two application messages under CTR, same nonce field.
- XOR the ciphertexts → P1 XOR P2.
- crib-drag with 'flag{' and 'Content-Type' reveals both plaintexts.

## 5. The verify endpoint that extends (length extension)

`mac = sha1(secret || role=user)`. Forge `role=user||glue||&role=admin`.
- Iterate --secret-len 8..32 until a forge verifies.

## 6. Where nothing works

AES-GCM with random nonces, tag checked before decrypt: every corruption
rejected identically. The class is closed — the write-up instead hunts key
material in the handout. Recorded as a negative in field-notes.
