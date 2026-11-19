# Field notes (deep) — how a web3 solve feeds back

## What a solve records

```text
the challenge        — the Setup + the Challenge
the predicate        — the exact isSolved() expression
the class            — the bug class that solved it
the chain            — the ordered txs + the attack contract if any
the evidence         — isSolved() false → true, the receipts
the lesson           — what the corpus didn't already say
```

`../field-notes.md` (the skill root) accumulates the `proposed` entries; a
`confirmed` entry is the checked lesson. `../../../LEARNING_LOOP.md` is the
promotion rule.

## What a web3 solve teaches the corpus

- a bug-class the catalogue didn't cover — a new file or a new variant
- a falsifier that was wrong — the class was closable differently
- a tooling gap — a `cast`/`forge` invocation that worked, a decompiler that
  helped
- a chain shape — two bugs the corpus lists separately that compose

## The catalogue-honest rule

The whole corpus is published knowledge — Ethernaut/CTF/Damn-Vulnerable-DeFi
shapes. A solve's `../field-notes.md` entry is what distinguishes "we read about
reentrancy" from "we solved one." Until a solve lands, the class stays
`catalogue` — the corpus is a starting point, not proof.

## The classify_solve loop

```bash
python3 tools/classify_solve.py --chain <id>     # files the solve into web-web3
```

The solve's chain card (`knowledge/chains/`) records the predicate→transition
map; this file's `verified-chains.md` updates from `catalogue` to `verified`.

## The "the corpus was wrong" case

A solve that broke a module's claim (a `selfdestruct` that didn't delete,
a `blockhash` that wasn't `0`, a transfer that allowed reentrancy) → the
field-note records the real behavior and the module gets corrected. The
on-chain behavior is the ground truth — the catalogue approximates it.
