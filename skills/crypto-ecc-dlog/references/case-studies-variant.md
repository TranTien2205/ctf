# Case studies variant — the shapes with the decision marked

## "The reused key" — `ecdsa-nonce-reuse`

Two `r`s equal → closed form → `d` → forge/decrypt. The `r` dedupe decided
everything; `z`/`order` were the only ways to fail.

## "The weak RNG" — `hnp-ecdsa`

`k = time(NULL)` or counter → `hnp-ecdsa --nonce-bound <range>` → `d`.
The bound read decided; `required_signatures` gave the count.

## "The DIY curve" — defect family

`Δ == 0` → `singular_ec`; `#E == p` → `smart_attack`; `#E` smooth → PH;
else generic-hard → protocol bug.

## "The point oracle" — invalid curve

Unvalidated `d·P'` → fake curves `E'_i` smooth `ord` → `d mod m_i` → CRT.

## "The biased LSB/MSB" — `hnp`

`k` MSB/LSB leaked → `(t,u)` → `hnp` with `B` on the unknown part.

## "The tiny subgroup" — `bsgs`/`pohlig`

`ord(g)` small inside big `p` → solve in `<g>`.

## "The pairing curve" — MOV

`#E` small embedding degree → MOV to `F_{p^k}` — no tool here; flag as
intended-path note.

## The shared close

Every case ends `x·G == Q`/`g^x == h` then `flag{`.
