# Evidence index — the proof components → the files

## The two evidence kinds → files

| Kind | Files |
|---|---|
| `class` (the scalar + verify) | `evidence*.md`,`verify*.md` |
| `impact` (the flag) | `evidence*.md`,`multi-step-chains*.md` |

## The `post-probe` shape → files

| Component | Files |
|---|---|
| `hypothesis-id` | `evidence*.md` |
| `--class crypto-ecc-dlog` | `evidence*.md` |
| `--evidence-kind` | `evidence*.md` |
| `--evidence` (verbatim) | `evidence*.md`,`verify*.md` |
| `--response` (the bytes) | `evidence*.md` |

## The record → files

| Record | Files |
|---|---|
| `../field-notes.md` | `field-notes-index.md` |
| `attempts` | `negative-results*.md` |
| `chains` | `verified-chains*.md` |
| `classify_solve` | `verified-chains*.md` |

## The discipline → files

| Rule | Files |
|---|---|
| evidence ⊆ response | `evidence*.md` |
| scalar ≠ flag | `evidence*.md`,`verify*.md` |
| falsifier ends it | `falsifiers*.md`,`negative-results*.md` |
