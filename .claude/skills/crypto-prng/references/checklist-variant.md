# Checklist variant — the abbreviated gate list

## The five-line gate

```
[ ] gen?       lcg/lfsr/mt/xorshift/seed — NOT urandom/secrets
[ ] count?     3/6/req/2w/624/4 — met
[ ] raw?       ints, consecutive, no gaps, no reseed
[ ] params?    m | a,c | taps,width | low-bits | seed window — known
[ ] verify?    predict == held-back — the plan exists
```

## The command check

```
[ ] crypto_attack.py <id> --<real-flags>     # no invented flags
[ ] tools/crypto/xorshift128.py --outs --predict   # the standalone
```

## The close check

```
[ ] predict==held → use → flag{ → post-probe/pre-flag → record
[ ] falsifier → attempts + reopen_if → decide.py rung
```

## The budget check

```
[ ] <5 probes on this mechanism
[ ] <15 min on this mechanism
[ ] falsifier → record, don't re-run the same model
```

## The honest check

```
[ ] a flag only from a live response / supplied artifact
[ ] predict==held before calling the state recovered
[ ] no flag{ from the description text
```
