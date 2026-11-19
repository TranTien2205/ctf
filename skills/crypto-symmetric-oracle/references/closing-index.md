# Closing index — the whole corpus by question

## "Which oracle do I have?"
`detection.md` → `oracle-shapes.md` → `encrypt-oracle-recon.md` /
`decrypt-oracle.md` / `verify-oracle.md`

## "It's ECB — now what?"
`ecb-detection.md` → `ecb-byte-at-a-time.md` (chosen-plaintext secret) or
`ecb-cut-and-paste.md` (token forgery) → `tools-ecb-oracle.md`

## "It's CBC — now what?"
`cbc-padding-oracle.md` (two distinct error answers) or `cbc-bitflip.md`
(unauthenticated edits) or `cbc-iv-equals-key.md` (IV bugs)

## "It's a stream — now what?"
`ctr-nonce-reuse.md` → `crib-drag.md` / `stream-integrity.md`

## "It's a MAC — now what?"
`hmac-vs-raw-mac.md` → `length-extension.md` / `mac-forgery.md` /
`verify-oracle.md` / `cbc-mac.md`

## "It has a tag and a nonce"
`gcm-nonce-reuse.md` → `tools-gcm-nonce.md`

## "Nothing leaks"
`authenticated-boundary.md` → `key-path.md` → reclassify

## Discipline
`evidence.md` · `falsifiers.md` · `negative-results.md` · `preconditions.md`
· `boundary-cases.md` · `edge-cases.md` · `anti-patterns.md` ·
`common-mistakes.md` · `troubleshoot.md` · `evasion.md` · `operator-notes.md`

## Maps
`per-boundary.md` · `per-condition.md` · `per-probe.md` · `per-signal.md`
· `attack-catalogue.md` · `recon-order.md` · `workflow.md` ·
`multi-step-chains.md` · `case-studies.md` · `worked-examples.md` ·
`theory.md` · `glossary.md` · `field-manual.md`
