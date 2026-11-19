# web-cors — reference index

A catalogue class: a foreign-origin page reads an authenticated
cross-origin response — the ACAO allows your origin AND ACAC lets
the session cookie ride.

## Start here

- `workflow.md` — the end-to-end loop: measure ACAO+ACAC → find the
  origin-check gap → build the page → deliver → exfil
- `cheatsheet.md` — the one-page reference
- `summary.md` — the class condensed
- `field-manual.md` — the tactical runbook
- `common-questions.md` — the confusions answered

## The gates — the check-shape modules

- `acao-deep.md` — the `Access-Control-Allow-Origin` value families
- `acac-and-credentials.md` — the `Access-Control-Allow-Credentials`
  gate and the credential sources
- `origin-check-deep.md` — every check shape: reflect/null/prefix/
  suffix/substring/subdomain/regex/url-parse — and its bypass
- `preflight-deep.md` — the OPTIONS gate for non-simple requests
- `headers-reference.md` — every CORS header and what it does
- `detection-deep.md` — every detection surface, black-box and white-box
- `vary-and-cache.md` — the `Vary: Origin` and cache-poison surface

## The exploit-side modules

- `exploit-page-patterns.md` — complete copyable read pages per shape
- `fetch-api-notes.md` — the exact JS that makes the read
- `delivery-contexts.md` — how the exploit page reaches the victim
- `bot-delivery.md` — the victim-viewer that carries the session
- `read-oracles.md` — proving the read actually happened
- `sensitive-endpoints.md` — the read targets that carry the flag
- `cors-chains.md` — the read feeding the next primitive
- `exploitation.md` — the exploitation walkthrough

## The context modules

- `framework-matrix.md` — the CORS surface per framework
- `browser-behavior.md` — per-engine edge cases
- `real-world-patterns.md` — the misconfigs that recur
- `ctf-shapes.md` — how the CTF CORS challenge is laid out
- `case-studies.md` — worked end-to-end walkthroughs
- `whitebox-hunt.md` — the source-driven pass
- `theory.md` — why CORS exists and breaks
- `glossary.md` — every term defined

## The boundary modules — the confusables

- `class-boundary.md` — CORS vs CSRF/XSS/XS-leaks/JSONP/ws/SSRF
- `interplay-matrix.md` — CORS plus the neighbors
- `alternate-reads.md` — JSONP/XSSI/postMessage/ws — the non-CORS channels
- `jsonp-and-alternates.md` — the script-tag read deep-dive
- `null-origin.md` — the opaque-origin shape
- `subdomain-bypass.md` — the subdomain-trust shape
- `acao-matrix.md` — the ACAO value matrix
- `origin-reflection.md` — the reflect shape
- `credentials-interplay.md` — the credential-interplay details
- `detection.md` — the detection overview
- `preflight.md` — the preflight overview

## The discipline modules

- `evidence-rules.md` — the proof standard for a CORS confirms
- `negative-results.md` — recording the gates that held
- `common-mistakes.md` — the ways the analysis goes wrong
- `error-analysis.md` — what each CORS error means
- `troubleshoot.md` — when the read doesn't work
- `audit-checklist.md` — the full verification sweep
- `payload-dictionary.md` — every probe and exploit shape
- `extended-corpus.md` — the complete signal/payload index
- `verified-chains.md` — the class's catalogue standing
- `writeup-techniques.md` — writeup-sourced techniques
- `workflow.md` — the loop
