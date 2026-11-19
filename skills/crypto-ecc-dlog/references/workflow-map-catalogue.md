# Workflow map catalogue — the scenario workflows indexed

## The "bare handout" workflow

| Step | Files |
|---|---|
| read | `detection*.md` |
| discriminate | `cipher-identification.md`,`detection-matrix.md` |
| solve | `payload-dictionary*.md` |
| verify | `verify*.md` |
| record | `field-notes-index.md` |

## The "signing oracle" workflow

| Step | Files |
|---|---|
| probe | `recon-order.md`,`scenarios*.md` |
| collect | `per-family-nonce.md` |
| solve | `ecdsa-nonce-reuse*.md`/`hnp-ecdsa*.md` |
| verify | `verify*.md` |
| forge | `multi-step-chains*.md` |

## The "dlog statement" workflow

| Step | Files |
|---|---|
| gate | `smoothness*.md` |
| solve | `pohlig-hellman*.md`/`bsgs*.md` |
| verify | `verify*.md` |
| use | `multi-step-chains*.md` |

## The "defect curve" workflow

| Step | Files |
|---|---|
| check | `per-check*.md` |
| solve | `smart-attack*.md`/`singular-ec*.md`/`invalid-curve*.md` |
| verify | `verify*.md` |

## The "stuck" workflow

| Step | Files |
|---|---|
| troubleshoot | `troubleshoot*.md` |
| falsify | `falsifiers*.md`,`per-falsifier.md` |
| record | `negative-results*.md` |
| escalate | `decide.py` rungs |
