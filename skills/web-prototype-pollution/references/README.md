# Prototype pollution reference map

This directory belongs to the canonical `web-prototype-pollution` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| A JSON body is merged into a server-side object (Node/JS) | `server-side-merge.md` |
| The target is Python and merge paths touch `__class__`, `__init__`, `__globals__` | `class-pollution-python.md` |
| Pollution happens in the browser via URL or client-side merge | `client-side-dom.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the pollution needs a concrete payload shape or a
confirm wording.

Every technique here was distilled from a field note in `../field-notes.md`;
the payloads below are the ones that actually worked on a live target.
