# Workflow index deep — phases → files → commands, annotated

## Phase: inventory

| Files | Command | Why |
|---|---|---|
| `detection*.md` | read | the artifact shapes |
| `recon-order*.md` | `ec.curve` | params + oracle probe |

## Phase: gates

| Files | Command | Why |
|---|---|---|
| `per-check*.md` | `r` dedupe | cheapest, highest value |
| `smoothness*.md` | `smoothness --n ord` | PH feasibility |
| `per-check*.md` | `Δ`/`#E`/`pow(h,ord,p)` | defect/subgroup |
| `per-boundary*.md` | `required_signatures` | lattice feasibility |

## Phase: solve

| Files | Command | Why |
|---|---|---|
| `payload-dictionary*.md` | `crypto_attack.py <id>` | the solve |
| `per-attack-*.md` | `tools/crypto/*.py` | module attacks |
| `multi-step-chains*.md` | composite | layered shapes |

## Phase: verify

| Files | Command | Why |
|---|---|---|
| `verify*.md` | `x·G == Q`/`pow` | the proof |

## Phase: record

| Files | Command | Why |
|---|---|---|
| `field-notes-index.md` | `post-probe` | the ledger |
| `negative-results*.md` | `attempts` | the no's |
| `verified-chains*.md` | `classify_solve` | the card |

## Phase: escalate

| Files | Command | Why |
|---|---|---|
| `falsifiers*.md`,`troubleshoot*.md` | `decide.py` | the rungs |
