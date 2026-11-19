# Falsifiers — the condition that closes each attack

## Per-attack falsifiers

| Attack | Falsifier — observe this, the attack is dead |
|---|---|
| `ecdsa-nonce-reuse` | no two `r` values equal → nonce wasn't reused |
| `hnp-ecdsa` | `d` fails `d·G == Q` after lattice → nonce wasn't biased, or bound/count wrong |
| `hnp` | same as hnp-ecdsa at the `(t,u)` level |
| `pohlig-hellman` | largest prime factor of `ord(g)` > ~2⁴⁰ → PH stalls; not this attack |
| `bsgs` | `ord(g)` or bound > ~2⁴⁴, or no collision → `x` outside range |
| `smoothness` | only a read — the falsifier lives in PH/BSGS |
| `smart_attack` | `#E ≠ p` → not anomalous |
| `singular_ec` | `Δ ≠ 0 mod p` → not singular |
| invalid curve | server validates points → impossible |

## The class falsifier

From the SKILL contract: *a scalar that does not reproduce the supplied
public key is not the key*. Every route ends at `x·G == Q` — a scalar that
fails it means a wrong attack, wrong `z`, wrong `order`, or a genuine dead
end (re-route: `decide.py`).

## The "budget spent" falsifier

Per AGENTS.md: 5 probes / 15 min per mechanism, 25/45 total. After the rungs
(`chain_match` → `reclassify` → `writeup_search` → `novel_plan` →
`fanout_sweep` → `solver_handoff`), `stop_report` — park with a falsifier
recorded in `knowledge/attempts/`.

## Recording a falsifier

`tools/state.py <challenge> --hypothesis … --verdict falsified` + a note in
`knowledge/attempts/<challenge>.json` with the measurement that killed it
and the precondition to reopen.
