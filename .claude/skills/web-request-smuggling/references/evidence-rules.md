# Evidence rules — what counts as a desync finding

## The bar — a desync produces a request the front never saw

The clean proof: a response that corresponds to NO request you sent —
or the next request's response carries the smuggle's output. A folded
character echo is a fold, not a smuggle.

## The confirms grade — the required signal

- a SECOND response to ONE request — the back-end answered a request
  the front never sent
- the NEXT request's response carries the smuggle's marker — the queue
  is poisoned
- the smuggle's `GET /internal` returns the internal route's content —
  the front filtered it, the back-end didn't

## The inconclusive grade — what does NOT prove desync

- a 302 — a redirect, could be the app's normal response
- a generic 400 — rejection, not desync — a strict parser rejecting a
  malformed request is a parser-error, not a smuggle
- a timeout alone — could be congestion — needs 3x repetition + absent
  on the control
- an echo of your input — reflection, not desync
- a folded-header echo — the fold landed, the smuggle may not have
- a 500 on the outer request — the front-end rejected the malformed
  request — no smuggle reached the back

## The response excerpt — the verbatim requirement

```bash
python3 tools/hooks.py post-probe <name> \
  --request "POST / HTTP/1.1 ... [desync body]" \
  --verdict confirms \
  --evidence-kind class \
  --class web-request-smuggling \
  --hypothesis-id h1 \
  --evidence "HTTP/1.1 404 Not Found" \
  --response "<the raw response bytes>"
```

The `--evidence` must be a SUBSTRING of `--response` — the proving
excerpt — a status line, a marker, a header — verbatim.

## The self-poison confirmation — the readback probe

```text
POST / [desync] → send GET / → the GET's response is the smuggle's
```

The normal request returning the smuggle's output is the self-poison —
the queue is misaligned — `response-poisoning.md`.

## The fold-vs-smuggle distinction — the evidence gap

- a FOLD: `%0d%0a` lands → an injected header appears — proves CRLF
  injection, NOT a smuggle
- a SMUGGLE: the back-end runs a second request — proves desync

Both live here — the fold is the low bar (injection), the smuggle is
the high bar (desync) — grade them separately.

## The victim-impact — the queue-poison evidence

On a shared instance the smuggle poisons the NEXT victim — the evidence
is the victim's response carrying your smuggle's output — you don't
observe the victim's socket — you infer from the self-poison or a
stored readback.

## The no-confirm shapes — the negative results

Record each as `inconclusive` or `denies` — never `confirms`:

- front strips `%0d%0a` → 200 with the encoded literal — denies fold
- back rejects the smuggle → 400 on the outer — denies desync
- the connection closes after each request → no queue — denies smuggle
- the front re-parses the tunnel → the upgrade doesn't escape — denies
  upgrade-smuggle

## The chain card — `htb-weather-app-ssrf-crlf-request-smuggling-upsert`

`knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json`
— the verified chain — a CRLF-fold into an outbound request — read the
card's `first_confirming_probe` before inventing.
