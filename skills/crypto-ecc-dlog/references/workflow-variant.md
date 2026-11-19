# Workflow variant — the alternate paths

## The signature-first path

```
sigs → dedupe r → reuse? → ecdsa-nonce-reuse
                → distinct + bounded k → hnp-ecdsa
                → partial k → hnp
```

## The params-first path

```
params → Δ check → singular_ec
      → #E check → smart_attack
      → smoothness #E → pohlig-hellman (curve ops via ec.py)
      → else → bsgs / re-read
```

## The oracle-first path

```
service → probe sign(m) ×2 → deterministic? → nonce attacks
        → probe point validation → invalid curve
        → collect sigs → hnp-ecdsa
```

## The statement-first path

```
h = g^x mod p → smoothness (p-1) → pohlig-hellman
             → x bounded → bsgs
             → 2q order → re-route
```

## The recovery-first path

```
d recovered → forge sign → token → flag
x recovered → shared secret → decrypt → flag
k recovered → d → sign → flag
```

## The stuck path

```
verify fails → troubleshoot*.md → falsifiers*.md → decide.py → escalate
```
