# Evidence index — the proof components → the files

## The `class`-evidence components

| Component | The files |
|---|---|
| `cipher_id --text` | `detection*.md`,`evidence*.md` |
| IC/chi²/Kasiski/freq | `evidence*.md`,`detection-deep.md`,`theory*.md` |
| the verdict | `cipher-identification.md`,`evidence*.md` |
| the tuple | `evidence*.md`,`detection*.md` |

## The `impact`-evidence components

| Component | The files |
|---|---|
| `classical_solve` `pt` | `payload-dictionary*.md`,`evidence*.md` |
| `enc(pt)=ct` | `verify*.md`,`evidence*.md` |
| `flag{`/`CTF{` present | `evidence*.md`,`known-plaintext*.md` |

## The post-probe record

| Component | The files |
|---|---|
| `hypothesis-id` | `field-notes-catalogue.md`,`evidence*.md` |
| `class`/`impact` | `evidence*.md` |
| the `ct`+`pt`+tuple | `evidence*.md`,`field-notes-catalogue.md` |
| the chain card | `LEARNING_LOOP`,`classify_solve.py` |

## The live-versus-artifact

`tools/hooks.py` — the verdict on a live `ct`-response; a flag-shaped `ct`
isn't a flag — `evidence*.md`.
