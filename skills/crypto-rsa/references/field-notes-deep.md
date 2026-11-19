# Field notes deep — the learning loop for crypto-rsa

## The loop

`LEARNING_LOOP.md` governs: every real observation becomes a proposed note;
`LEARNING_LOOP` promotes a note to confirmed when it holds across runs; a
confirmed note may raise the class from `catalogue` to `verified`.

## The note shape for RSA

```
- <date> <challenge>:
  discriminator = <which attack-table row fired>
  attack        = <crypto_attack.py id>
  bound         = <the measured bound: d<n^0.25, window<n^0.25, e n's, ...>
  input         = <the leaked/observed values>
  recovered     = <p,q | d | m | a negative>
  verify        = <pow(m,e,n)==c | p*q==n | NONE — the falsifier observed>
  trap          = <what almost went wrong — a pad, a bound, a wrong root>
```

## What counts as confirmed

- `pow(m,e,n)==c` — a plaintext recovery.
- `p*q==n` — a factor recovery.
- `pow(c,d,n)==m` + `pow(m,e,n)==c` — a `d` recovery.
- A bound exceeded with the falsifier observed — a confirmed *negative*.

## What does not

- a flag-shaped string without `pow` — a decoy.
- an attack that "ran" — exit status is not evidence.
- a bound "close to" exceeded — the bound is binary.

## The standing gap

No `crypto-rsa` field note is confirmed yet — the class is `catalogue`. The
first real solve turns `../field-notes.md` into the experience record and may
raise the class via `tools/classify_solve.py`.
