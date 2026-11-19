# Worked examples — the numbers for each primitive

## Byte-at-a-time, byte by byte

Secret = 'flag{A}' appended to our input under ECB-16.

1. Input 'A'*15 → block 0 = 'AAAAAAAAAAAAAAAf'. Save ciphertext block C*.
2. Input 'A'*15 + 'f' → if block 0 == C*, byte 1 = 'f'. Try all 256.
3. Found at guess 102 ('f'). Input 'A'*14 → block 0 = 'AA...AAfl'. Guess 'l'
   at 108.
4. Continue: 'a'(97), 'g'(103), '{'(123), 'A'(65), '}'(125) — but the '}' is
   the 7th byte; once recovered plaintext ends the loop at the measured
   secret length.
5. Full recover: ~7 × 256 = 1,792 requests worst case.

## Padding oracle, one byte

CT = IV | C1 | C2, plaintext block P2. Want P2's last byte.

- For guess g in 0..255: send IV' | C1' | C2 where C1'[15] = C1[15] XOR
  0x01 XOR g (other C1' bytes unchanged for the last-byte round).
- The 'padding ok' answer says D(C2)[15] = g → P2[15] = g XOR C1[15].
- Byte 16 next: force pad \\x02\\x02 — set C1'[15] for known pad-2, sweep
  C1'[14].
- ~256 requests/byte worst, ~128 average.

## Length extension, one forge

mac = sha1(K || 'role=user'), |K| = 16.
- length-extension --hash sha1 --mac <mac> --secret-len 16 --orig 'role=user'
  --append '&role=admin'
- Emits: forged_mac and extended = 'role=user' || \\x80||zeros||len-block ||
  '&role=admin'.
- Submit extended + forged_mac; verifies because sha1 state after the glued
  block equals the original digest.

## Crib-drag, one offset

C1 XOR C2 at offset 0: XOR of two plaintexts.
- Try crib 'flag{': C1[0:5] XOR 'flag{' → produces 'GET /' → offset 0 of
  message 2 starts 'GET /' while message 1 starts 'flag{'.
- Extend: 'flag{A' → message 2 'GET /a' — confirms and grows both sides.
