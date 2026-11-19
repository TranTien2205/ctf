# Workflow map — phase → procedure → files

## The phase rows

| Phase | Procedure | Files |
|---|---|---|
| inventory | read handout, name group | `detection*.md`,`recon-order.md` |
| discriminate | gates → attack | `cipher-identification.md`,`detection-matrix.md`,`per-family-*.md` |
| solve | `crypto_attack.py <id>` | `payload-dictionary*.md`,`per-attack-*.md` |
| verify | `x·G == Q` / `g^x == h` | `verify*.md`,`evidence*.md` |
| record | `post-probe` + falsifier | `field-notes-index.md`,`negative-results*.md` |
| escalate | `decide.py` rungs | `falsifiers*.md`,`troubleshoot*.md` |

## The family workflows

| Family | Files |
|---|---|
| nonce | `per-family-nonce.md`,`ecdsa-nonce-reuse*.md`,`hnp*.md` |
| dlog | `per-family-dlog.md`,`pohlig-hellman*.md`,`bsgs*.md`,`smoothness*.md` |
| defect | `per-family-curve-defect.md`,`smart-*.md`,`singular-*.md`,`invalid-*.md` |

## The shape workflows

| Shape | Files |
|---|---|
| oracle | `recon-order.md`,`scenarios*.md` |
| layered | `multi-step-chains*.md` |
| layered-crypto→web | `multi-step-chains*.md` |
