# Workflow playbook — the procedures end to end

## The signature playbook

1. Inventory sigs; dedupe `r`.
2. `r` dup → `ecdsa-nonce-reuse --sigs f --order n`.
3. No dup + bounded `k` → `hnp-ecdsa --sigs f --order n --nonce-bits B`
   (count ≥ `required_signatures`).
4. Partial `k` → `hnp --t f --u f --modulus n --bound B`.
5. `d·G == Q` verify → forge/decrypt → `flag{`.

## The dlog playbook

1. `smoothness --n ord` → factor.
2. Smooth → `pohlig-hellman --g --h --p --order ord`.
3. `x` bounded → `bsgs --g --h --p --order bound`.
4. `pow(g, x, p) == h` → `x` → use.

## The curve playbook

1. `Δ mod p` — `0` → `singular_ec`.
2. `#E` — `== p` → `smart_attack`.
3. `smoothness --n #E` → `pohlig-hellman` on curve.
4. `x` bounded → `bsgs` with point ops.
5. `x·G == Q` verify.

## The oracle playbook

1. `sign(m)` ×2 → determinism read.
2. Collect sigs → nonce family.
3. `multiply(P')` → validation read → invalid curve if absent.

## The close playbook

`post-probe` → `../field-notes.md` → `classify_solve.py`/`attempts` →
`decide.py` if stuck.
