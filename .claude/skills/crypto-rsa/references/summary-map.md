# Summary map — the one-line index

## The pipeline

```
sheet → discriminate → bound-check → attack → pow-verify → record
```

## The class

`crypto-rsa` — RSA key or plaintext recovery. Catalogue — no local solve.

## The files by job

- **model**: `onboarding`,`mechanism`,`mechanism-deep`,`theory`,`summary`,`glossary`,`quick-reference`
- **detect**: `detection`+variants,`parameter-sheet`,`recon-order`,`detection-matrix`,`detection-checklist`
- **attack ids**: `attack-table`,`attack-table-deep`,`attack-families`,`attack-shapes`,`extended-corpus`,`deep-dives`
- **per-attack**: `batch-gcd`,`common-modulus`,`fermat`,`wiener`,`boneh-durfee`,`coppersmith`,`small-e-root`,`hastad`,`pollard-pm1`,`franklin-reiter`,`crt`,`factor-from-d`
- **bounds**: `lattice-bounds`,`per-bound`,`falsifiers`,`falsifier-map`,`boundary-cases`
- **maps**: `per-attack`,`per-parameter`,`per-signal`,`per-mechanism`,`per-bound`,`per-endpoint`,`per-class`,`per-target`,`per-form`,`per-channel`,`per-check`,`per-condition`,`per-falsifier`,`per-route`,`per-vector`,`detection-map`,`mechanism-map`,`theory-map`,`evidence-map`,`negative-map`,`payload-map`,`workflow-map`,`summary-map`,`map-index`,`decision-table`
- **procedure**: `workflow`,`workflow-deep`,`workflow-map`,`workflow-index`,`workflow-playbook`,`first-hour`,`field-manual`,`field-manual-deep`,`operator-notes`,`exploitation`,`exploitation-deep`,`exploitation-catalogue`,`payload-dictionary`,`payload-map`,`payload-families`,`payload-variants`,`probe-catalogue`,`probe-map`,`multi-step-chains`,`extended`
- **evidence**: `evidence-rules`,`evidence-deep`,`evidence-catalogue`,`evidence-map`,`evidence-playbook`,`verify`,`verification-protocol`,`falsifiers`,`negative-results`,`negative-map`
- **discipline**: `edge-cases`,`edge-cases-deep`,`common-mistakes`,`common-mistakes-deep`,`anti-patterns`,`troubleshoot`,`troubleshoot-deep`,`common-questions`,`common-questions-deep`,`evasion`,`evasion-deep`,`boundary-cases`,`boundary-cases-deep`,`class-boundary`,`per-boundary`,`preconditions`,`checklist`,`closing-notes`
- **cases**: `case-studies`,`case-studies-deep`,`worked-examples`,`worked-examples-deep`,`real-world-cases`,`scenarios`,`verified-chains`
- **index**: `README`,`README-deep`,`index`,`closing-index`,`map-index`,`field-notes-deep`

## The verify

`pow(m,e,n)==c` · `p*q==n`. The falsifier is the attack's bound.
