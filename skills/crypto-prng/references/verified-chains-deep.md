# Verified chains deep — the honest status, expanded

## The status

**Zero `crypto-prng` chain cards exist in `knowledge/chains/`.** The
class is `catalogue` — the corpus is standard published mechanism +
field procedure, NOT locally-verified experience. Every statement here is
mechanism truth, not "we did this here".

## Why the status matters

A `catalogue` class's content is published knowledge — correct but
unproven HERE. A `verified` class has a `knowledge/chains/` card proving
it was solved here. The gate (`pre-flag`/`post-probe`) is the same
either way — the difference is the confidence a card confers.

## What a real card would carry

```json
{
  "id": "prng-<slug>",
  "class": "crypto-prng",
  "signals": ["getrandbits", "session_id", "mt19937"],
  "chain": ["collect 624 consecutive getrandbits(32) words",
            "crypto_attack.py mt19937-clone --outputs-file outs.txt --count 1",
            "predict_next == o624", "forge admin session id", "flag"],
  "first_confirming_probe": "crypto_attack.py mt19937-clone --outputs-file outs.txt",
  "falsifier": "predict_next != o624 — <624/non-raw/gap/reseed",
  "blast_radius": "read-only offline math; the collection is the only request cost"
}
```

## The card's role

- `signals` — the observable cues that fired the match.
- `chain` — the ordered steps.
- `first_confirming_probe` — the command to run FIRST.
- `falsifier` — the kill condition + what it means.
- `blast_radius` — the request cost.

## The patterns a card would capture

| Pattern | Signals | Chain |
|---|---|---|
| LCG token | `token`,`a·x+c`,`m` | `lcg-recover`→predict→forge→flag |
| LFSR cipher | `ct`,`flag{` prefix | BM→`lfsr-predict`→⊕→flag |
| MT session | `getrandbits`,`session` | 624→clone→predict→hijack→flag |
| seed token | `iat`,`random`,`time` | window→enumerate→match→flag |
| truncated | `nextInt`,`x>>16` | `lcg-truncated --low-bits 16`→key→flag |

## The traps a card records

- the normalization that was needed (float→word, hex→int).
- the convention that bit (`--low-bits`/`--taps`).
- the count floor barely met or missed.
- the variant (`mt_rand`/`128+`/`java.util.Random`) that wasn't the
  plain algorithm.

## The promote path

Solve → `classify_solve` → `knowledge/chains/<id>` card → `../field-notes.md`
`confirmed` → the class promotes `catalogue`→`verified`.

Fail → `attempts/<challenge>.json` with the falsifier + `reopen_if` —
the kill map so the next attempt doesn't re-walk dead layers.
