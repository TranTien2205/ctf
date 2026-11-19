# Workflow catalogue deep — every shape's full procedure

## The bare-handout procedure, expanded

```
handout → detection*.md reads → cipher-identification.md discriminate
→ payload-dictionary*.md command → verify*.md check → field-notes-index.md record
```

Every step has its own file — the corpus navigates itself.

## The oracle procedure, expanded

```
service → recon-order*.md probe (determinism, validation)
→ sigs collected → per-family-nonce.md route
→ ecdsa-nonce-reuse/hnp-ecdsa/hnp → verify → forge → flag
```

## The dlog procedure, expanded

```
h = g^x mod p → smoothness --n ord →
  largest ≤ 2⁴⁰ → pohlig-hellman → x → verify → use
  bounded x → bsgs → x → verify → use
  2q → re-read — the bug isn't dlog
```

## The defect procedure, expanded

```
p a b → Δ check → 0? → singular_ec
    → #E == p? → smart_attack
    → #E smooth → pohlig-hellman (ec.py ops)
    → else → bsgs / protocol
```

## The invalid-curve procedure, expanded

```
multiply(P) → submit off-curve P' → accepted?
→ ec.py fake curves E'_i smooth ord
→ bsgs/pohlig per response → CRT → d → verify → flag
```

## The stuck procedure, expanded

```
verify fails → troubleshoot*.md fix
            → falsifiers*.md kill-condition
            → negative-results*.md record
            → decide.py rungs
```
