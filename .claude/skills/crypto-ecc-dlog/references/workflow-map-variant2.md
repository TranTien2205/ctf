# Workflow map variant 2 — the phase graph, compact restatement

## The happy path

```
read → gate → route → solve → verify → flag → record
```

## The files on the happy path

- read — `detection*.md`,`recon-order*.md`.
- gate — `per-check*.md`,`per-boundary*.md`,`detection-checklist*.md`.
- route — `per-family-*.md`,`per-attack-*.md`,`cipher-identification.md`.
- solve — `payload-dictionary*.md`,`workflow*.md`,`*-deep.md`.
- verify — `verify*.md`,`per-check*.md`.
- flag — `evidence*.md`,`multi-step-chains*.md`.
- record — `field-notes-*.md`,`verified-chains*.md`.

## The unhappy path

```
solve → verify-fail → troubleshoot* → fix | falsifiers* → attempts → decide.py
```

## The files on the unhappy path

- fix — `troubleshoot*.md`,`common-mistakes*.md`.
- falsify — `falsifiers*.md`,`per-falsifier.md`.
- record-no — `negative-results*.md`.
- next — `decide.py`.
