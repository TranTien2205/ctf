# Evidence rules — what proves what, at which level

The proof-ladder — each level needs its own evidence — the
substring-check binds the claim to the bytes — no retyped
excerpts, no asserted content.

---

## 1. The three evidence-levels

```text
SURFACE — "the shape exists"
  what it is: the url-param is present, the form renders, the
              endpoint accepts the field — the HINT — the classifier
              saw it — never a confirm
  examples: "the /fetch endpoint takes url=", "the form posts a
             url-field", "the webhook-form exists"
  verdict:  never confirms — surface-only — the class isn't shown

CLASS — "the server fetched"
  what it is: the server DIALED — the outbound-request happened —
              the fetch is real — the class exists
  what proves it:
    - a refused-error — "Connection refused" means the fetcher
      dialled — the error is fetch-evidence
    - a callback — your listener got the hit — the source-ip +
      headers + the fetcher's UA
    - a differential — internal-A answers differently than
      internal-B — the dial is the difference
    - a timing-delta — the fetch's latency vs an unfetchable —
      the dial-attempt's timing
  verdict:  confirms the CLASS — "ssrf exists" — the bug-class
            is live — but says nothing about the flag yet

IMPACT — "the internal-content was read"
  what it is: the flag's bytes, the internal-route's content, the
              metadata, the file-contents — the flag-level reach
  what proves it:
    - the flag-string in a fetched-response — verbatim — the
      response bound to the claim
    - an internal-route's unique-content — the admin-panel's html
    - the metadata-content — user-data/iam-creds
    - the file-contents — /etc/passwd lines, /flag's bytes
  verdict:  the flag-level claim — "ssrf reached the flag" —
            the solving evidence
```

## 2. The binding — the response-evidence link

```text
the evidence must be a SUBSTRING of the response — post-probe
checks it — the quote has to be verbatim bytes from the answer:
  --response '<the actual response bytes>'
  --evidence 'the verbatim excerpt'
the gate rejects a claim whose "evidence" isn't in the response —
the check is mechanical — the quote can't be paraphrased
```

`http_probe.py` is the sanctioned path — it holds request+response
together and emits the post-probe command with `--response` filled
— paste the command, don't reconstruct it.

## 3. The non-proofs — what never confirms

```text
- a flag-shaped string in SOURCE/CONFIG — a candidate — the flag
  must come from a live-response or supplied-artifact — the
  source is static — the flag must be READ through the ssrf
- a callback that shows the fetch happened — proves the CLASS —
  not the impact — "the server fetched my-url" ≠ "the server read
  the flag" — the callback is class-evidence
- a timing-difference — an oracle — the timing answers a question —
  one bit — never "the flag" — the answer is binary not the bytes
- the "fetch succeeded" — the fetch happened — class-evidence —
  not impact
- the "200 on /admin" — a status — the route exists — class-ish —
  the route's CONTENT is the impact
- a guess — "the flag is probably at /flag" — speculation — never
```

## 4. The partial-proofs — the mid-level signals

```text
the refused-error on 127.0.0.1:1   → the fetch dials loopback —
                                      class-evidence
the open-port differential          → the port-oracle — the map —
                                      class + recon
the metadata-IP reachable           → the cloud-context — the
                                      fetch reaches link-local —
                                      class + the metadata-chain
                                      is OPEN
the internal-route's html           → the route's content — impact
the file-content                    → the read — impact
the redis-key's value               → the store-content — impact
the creds in metadata               → the creds — impact (they're
                                      usable creds)
```

## 5. The pre-flag gate — the flag-verification

```bash
python3 tools/hooks.py pre-flag $C --value "flag{...}" \
  --source "<the-response-or-artifact-it-came-from>"
# the flag must appear in a LIVE response or a supplied artifact —
# the gate checks the flag-string is in the source — a flag you
# "reconstructed" or "guessed" fails — the gate is the proof
```

## 6. The provenance-record — the ledger writes

```bash
# a class-confirm
python3 tools/hooks.py post-probe $C \
  --hypothesis-id H1 --class web-ssrf --verdict confirms \
  --evidence-kind class --evidence 'Connection refused' \
  --response 'the actual error-response bytes'

# an impact-confirm
python3 tools/hooks.py post-probe $C \
  --hypothesis-id H2 --class web-ssrf --verdict confirms \
  --evidence-kind impact --evidence 'flag{...}' \
  --response 'the response carrying the flag'
```

## 7. The verbatim-excerpt rules

```text
- quote EXACTLY — the substring-check — bytes not summary
- the excerpt is the SMALLEST proving-fragment — "flag{...}" or
  "Connection refused" — enough to be unique — not the whole body
- the excerpt must be IN the response — the tool binds them —
  don't paste the excerpt from memory
- an error-response IS a response — the refused-error counts —
  the "response" is whatever the fetch returned
- a timeout is NEVER a response — no-bytes is no-evidence —
  timeout is inconclusive always
```

## 8. The differential-evidence — the comparison

```text
the paired-probe — two responses that differ:
  url=http://127.0.0.1:1/  → "refused"
  url=http://127.0.0.1:80/ → "connect" or content
the DIFFERENCE is the evidence — the dial is shown by the split —
record BOTH responses — the ledger needs the pair — "port-1
refused, port-80 answered" is the class-proof — a single refused
is the same — the pair makes it undeniable
```

## 9. The negative-evidence — the falsifiers

```text
record negatives too — the classes you CLOSED:
  "file:// rejected with 'scheme not allowed'" → the file-scheme
  is dead → the file-family is out — a proved-negative — the
  ledger holds it — sanitizer_fuzz records negatives
  "the callback never fired across 3 probes AND internal refused"
   → no-fetch → the class is dead — the falsifier
  "the rebind answers identically twice" → no-split → the rebind
   dies — a measured-negative
```

## 10. The verdict-mapping — what to report

```text
the evidence-level decides the verdict's strength:
  surface   → inconclusive or a surface-note — never confirms
  class     → confirms the CLASS — "web-ssrf is live" — the bug-
              class confirmed — not yet the flag
  impact    → confirms the IMPACT — "the flag was read" — the
              solving-level — the claim carries the flag-bytes
the verdict-word and the evidence-kind must match — a 'class'
verdict carries class-evidence — an 'impact' verdict carries the
flag-bytes — mismatched claims fail
```
