# Detection playbook variant — the procedure with branches spelled out

## Step 0 — classify the artifact

- `sigs` file / endpoint → nonce branch.
- `params` → defect branch.
- `h = g^x` statement → dlog branch.
- oracle → curve-oracle branch.

## Step 1 — nonce branch

```
r dup? → ecdsa-nonce-reuse --sigs f --order n
k hinted bounded? → hnp-ecdsa --sigs f --order n --nonce-bits B
k partial? → hnp --t --u --modulus n --bound B
else → look elsewhere
```

## Step 2 — dlog branch

```
smoothness --n ord → largest ≤ 2⁴⁰? → pohlig-hellman
x bounded? → bsgs --order bound
else → defect or protocol
```

## Step 3 — defect branch

```
Δ == 0? → singular_ec
#E == p? → smart_attack
#E smooth? → pohlig-hellman on curve
server unvalidated? → invalid curve
```

## Step 4 — oracle branch

```
sign(m)×2 → same? deterministic; different? random/biased → hnp-ecdsa
point P' accepted? → invalid curve; rejected? → validation ok → dead
```

## Step 5 — the verify

`x·G == Q`/`g^x == h` — always.

## Step 6 — the record

`post-probe` + `../field-notes.md` + falsifier on fail.
