# Workflow variant 2 — alternate procedure routes

## The "two sigs" fast path

```
sigs → r equal? → ecdsa-nonce-reuse --sigs f --order n → d → verify → flag
```

The single-command solve — check it first always.

## The "many sigs" path

```
sigs → r distinct →
  k bounded? → hnp-ecdsa --sigs f --order n --nonce-bits B
  k partial? → hnp --t f --u f --modulus n --bound B
  k fine? → not nonce — look elsewhere
```

## The "custom curve" path

```
params → Δ? → singular_ec
      → #E == p? → smart_attack
      → #E smooth? → pohlig-hellman (ec.py ops)
      → else → bsgs or protocol
```

## The "service" path

```
sign(m)×2 → deterministic? → collect sigs → hnp-ecdsa
multiply(P') → accepted? → invalid curve → CRT
```

## The "statement" path

```
h = g^x mod p → smoothness → pohlig-hellman / bsgs
```

## The "stuck" path

```
verify fails → troubleshoot* → falsifiers* → decide.py → escalate rungs
```

## The "close" path

```
flag → post-probe → field-notes → classify_solve / attempts
```
