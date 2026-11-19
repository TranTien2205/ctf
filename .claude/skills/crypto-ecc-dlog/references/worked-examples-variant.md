# Worked examples variant — narrated with the decision points

## `ecdsa-nonce-reuse`

Handout: two JWTs, `sig = r||s`, `r` identical on both. Extract `z` =
`int(sha256(header.payload))` truncated. `--sigs` file → one command → `d`
→ `d·G == Q` → forge `{"role":"admin"}` → flag.

**The decision:** `r` identical → reuse, not bias.

## `hnp-ecdsa`

Service `sign(m)` on P-256, challenge says "nonce is 128-bit". `z` =
`sha256(m)` truncated. Collect 6 sigs (`required_signatures(256,128)` ≈ 4
+ margin). `hnp-ecdsa --sigs f --order n --nonce-bits 128 --curve secp256r1
--pubkey 04...` → `d` → verify → flag.

**The decision:** bound from the statement; count from the formula.

## `pohlig-hellman`

`h = g^x mod p`, `p-1 = 2²·3·5·131`. `smoothness` confirms largest factor
131 → `pohlig-hellman --g --h --p --order (p-1)` → `x` → `pow(g,x,p)==h`
→ `x` is the key → decrypt → flag.

**The decision:** smoothness gate, not `bsgs` blind.

## `bsgs`

`x` stated `< 2^20` → `bsgs --g --h --p --order 1048576` → `x` → verify.

**The decision:** bound stated → `--order` = bound.

## `smart_attack`

`p a b` custom, `#E == p` → `smart_attack.py` → `x` → `x·P == Q` → flag.

**The decision:** `#E` count is the gate.

## `singular_ec`

`Δ ≡ 0` → `singular_ec.py` → `x` → `x·P == Q` → flag.

## invalid curve

`multiply(P')` accepts off-curve → `ec.py` fake curves with smooth `ord(P'_i)`
→ `bsgs` per response → CRT → `d` → `d·G == Q` → flag.
