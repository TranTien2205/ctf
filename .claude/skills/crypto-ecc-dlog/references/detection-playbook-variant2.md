# Detection playbook variant 2 — the branch procedures compact

## Signature branch compact

```
sigs → Counter(r)
  dup? → ecdsa-nonce-reuse
  all distinct → k bound? → hnp-ecdsa | partial k? → hnp | else dead
```

## Dlog branch compact

```
h = g^x → smoothness ord
  ≤2⁴⁰ → pohlig-hellman
  x bounded → bsgs
  2q/else → not dlog
```

## Defect branch compact

```
params → Δ==0? → singular_ec
      → #E==p? → smart_attack
      → #E smooth? → pohlig-hellman (ec.py)
      → unvalidated P? → invalid curve
```

## Close branch compact

```
scalar → x·G == Q | pow(g,x,p) == h → flag{ → post-probe → field-notes
fail → troubleshoot* → falsifiers* → attempts → decide.py
```
