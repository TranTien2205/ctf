# Workflow playbook variant — the procedures restated compactly

## Nonce playbook

```
dedupe r → reuse? → ecdsa-nonce-reuse
        → k bound? → hnp-ecdsa --nonce-*
        → partial k? → hnp --t --u
        → else → not nonce
```

## Dlog playbook

```
smoothness ord → ≤2⁴⁰? → pohlig-hellman
              → x bounded? → bsgs
              → else → defect/protocol
```

## Defect playbook

```
Δ? → singular_ec
#E == p? → smart_attack
#E smooth? → pohlig-hellman (curve)
unvalidated? → invalid curve
```

## Verify playbook

```
x·G == Q | pow(g,x,p) == h → flag step → flag{...}
```

## Record playbook

```
post-probe → field-notes → classify_solve/attempts → decide.py
```

## Stuck playbook

```
troubleshoot* → falsifiers* → negative-results* → decide.py rungs
```
