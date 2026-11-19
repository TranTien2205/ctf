# Detection checklist variant — the read-run-list, compact

## Artifact reads

- [ ] `p a b G n Q`/`g h` extracted.
- [ ] sigs extracted (file for `--sigs`).
- [ ] `z`/`m` identified.
- [ ] oracle endpoints noted.

## Gate reads

- [ ] `r` dedupe run.
- [ ] `smoothness --n ord` run.
- [ ] `Δ = 4a³+27b² mod p` checked.
- [ ] `#E` counted/checked vs `p`.
- [ ] `k`/`x` bound read.
- [ ] `required_signatures` computed.
- [ ] validation probed.

## Route reads

- [ ] family picked (nonce/dlog/defect).
- [ ] attack picked (`per-attack-*`).
- [ ] command composed (`payload-dictionary*`).

## Close reads

- [ ] verify planned (`x·G == Q`/`pow`).
- [ ] flag shape expected.
- [ ] `post-probe` shape ready.
