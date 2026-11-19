# web-cors — reference index

A catalogue class: a foreign-origin page reads an authenticated
cross-origin response — the ACAO allows your origin AND ACAC lets
the session cookie ride.

## Start here

- `workflow.md` — the end-to-end loop: measure → find the gap → build →
  deliver → exfil
- `cheatsheet.md` — the one-page reference
- `quick-reference.md` — the field card
- `reference-card.md` — the condensed lookup card
- `summary.md` — the class condensed
- `field-manual.md` — the tactical runbook
- `common-questions.md` — the confusions answered
- `methodology.md` — the ordered, bounded procedure

## The gates — the check-shape modules

- `acao-deep.md` — the `Access-Control-Allow-Origin` value families
- `acao-matrix.md` — the ACAO value matrix
- `acac-and-credentials.md` — the ACAC gate and the credential sources
- `origin-check-deep.md` — every check shape and its bypass
- `origin-reflection.md` — the reflect shape
- `origin-values-corpus.md` — the complete bypass battery, categorized
- `preflight-deep.md` — the OPTIONS gate for non-simple requests
- `preflight.md` — the preflight overview
- `headers-reference.md` — every CORS header
- `cookie-and-session.md` — the credential that rides
- `credentials-interplay.md` — the credential-interplay details
- `detection-deep.md` — every detection surface
- `detection.md` — the detection overview
- `detection-checklist.md` — the full detection sweep
- `vary-and-cache.md` — the `Vary` and cache-poison surface

## The exploit-side modules

- `exploit-page-patterns.md` — complete copyable read pages per shape
- `poc-collection.md` — working exploit pages for every shape
- `fetch-api-notes.md` — the exact JS that makes the read
- `exfil-channels.md` — every way the data leaves
- `delivery-contexts.md` — how the page reaches the victim
- `bot-delivery.md` — the victim-viewer carrying the session
- `read-oracles.md` — proving the read happened
- `sensitive-endpoints.md` — the read targets carrying the flag
- `cors-chains.md` — the read feeding the next primitive
- `exploitation.md` — the exploitation walkthrough
- `advanced-techniques.md` — the non-obvious attacks
- `payload-dictionary.md` — every probe and exploit shape
- `payload-variants.md` — the complete payload catalog
- `extended-corpus.md` — the complete signal/payload index

## The context modules

- `per-stack-deep.md` — the misconfig, framework by framework
- `framework-matrix.md` — the CORS surface per framework
- `browser-behavior.md` — per-engine edge cases
- `real-world-patterns.md` — the misconfigs that recur
- `ctf-shapes.md` — how the CTF CORS challenge is laid out
- `case-studies.md` — worked end-to-end walkthroughs
- `scenarios.md` — the challenge played out in full
- `walkthroughs.md` — complete probe-to-flag solves
- `whitebox-hunt.md` — the source-driven pass
- `theory.md` — why CORS exists and breaks
- `cors-reference.md` — the consolidated reference
- `glossary.md` — every term defined

## The boundary modules — the confusables

- `class-boundary.md` — CORS vs CSRF/XSS/XS-leaks/JSONP/ws/SSRF
- `interplay-matrix.md` — CORS plus the neighbors
- `alternate-reads.md` — JSONP/XSSI/postMessage/ws
- `jsonp-and-alternates.md` — the script-tag read deep-dive
- `null-origin.md` — the opaque-origin shape
- `subdomain-bypass.md` — the subdomain-trust shape
- `attack-surface.md` — the complete entry-point inventory
- `edge-cases.md` — the corners that catch you

## The discipline modules

- `evidence-rules.md` — the proof standard for a CORS confirms
- `negative-results.md` — recording the gates that held
- `common-mistakes.md` — the ways the analysis goes wrong
- `error-analysis.md` — what each CORS error means
- `troubleshoot.md` — when the read doesn't work
- `troubleshoot-deep.md` — the failure modes, exhaustively
- `audit-checklist.md` — the full verification sweep
- `checklist-and-runbook.md` — the printable assessment
- `probing-patterns.md` — the systematic measurement
- `operator-notes.md` — the practical guidance
- `integration-notes.md` — the skill inside the control loop
- `verified-chains.md` — the class's catalogue standing
- `writeup-techniques.md` — writeup-sourced techniques
