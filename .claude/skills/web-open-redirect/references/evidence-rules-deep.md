# Evidence rules (deep) — the verbatim-Location standard in full

## The evidence hierarchy for open-redirect

```text
the verbatim Location: carrying the canary   <- the CLASS evidence (oracle)
the downstream laundered effect              <- the IMPACT evidence (chain)
the param/carrier presence                   <- the SURFACE evidence (not a confirm)
```

## The verbatim-Location standard

```text
the Location: header is the oracle — the verbatim bytes are the evidence:
  'Location: https://attacker.invalid/landing'   <- the class evidence
  'Location: https://evil.com'                   <- the simple-canary evidence
  'Location: //evil.com'                         <- the scheme-relative evidence
  'Location: https://target.com.evil.com'        <- the subdomain-gap evidence
```

The evidence is a SUBSTRING of the response — `post-probe --evidence` must
match `--response` verbatim.

## The post-probe command — the exact shape

```bash
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <id> \
  --class web-open-redirect \
  --verdict confirms \
  --evidence-kind class \
  --evidence 'Location: https://attacker.invalid/landing' \
  --response 'HTTP/1.1 302 Found
Location: https://attacker.invalid/landing
...'
```

The `--evidence` string must appear verbatim in `--response`. The gate
asserts the substring — a paraphrase fails.

## The evidence-kind split — class vs impact

```text
--evidence-kind class   <- the Location: oracle — the redirect IS
                           attacker-controlled
--evidence-kind impact  <- the laundered-trust effect — the OAuth code on
                           the canary, the fetched internal content, the
                           bot's visit
```

A `Location: <canary>` is `--evidence-kind class` (the class oracle); the
OAuth-code-on-the-canary is `--evidence-kind impact` (the chain's effect).

## The surface-vs-candidate boundary

```text
SURFACE (never a confirm):
  - the param name exists           -> ?next=
  - a 302 exists                    -> a redirect happens
  - the param "looks like" a redirect
  - the server "would" follow it
CANDIDATE (the class-confirm):
  - Location: <the-canary>          -> the verbatim header
  - content="0;url=<canary>"        -> the meta-refresh
  - location.href="<canary>"        -> the JS-nav
IMPACT (the chain-confirm):
  - the code/token lands on the canary
  - the fetcher reaches the internal host
  - the bot's visit logs on the canary
```

## The verbatim-carrier evidence — each carrier's form

```text
Location: header      -> 'Location: https://attacker.invalid/landing'
Refresh: header       -> 'Refresh: 0;url=https://attacker.invalid'
meta refresh          -> 'content="0;url=https://attacker.invalid"'
JS nav                -> 'location.href="https://attacker.invalid"'
                        'window.location="https://attacker.invalid"'
                        'location.replace("https://attacker.invalid")'
```

## The multi-status evidence — the redirect type

```text
302 Found        <- the common; the method drops on the follow
301 Moved Perm.  <- the permanent
303 See Other    <- the REST-shape
307 Temporary    <- keeps the method
308 Permanent    <- keeps the method
```

Record the status — a 302-on-POST drops the body; a 307 keeps it. For the
redirect-param surface the status is surface-detail; for a POST-carried
param it matters.

## The chain-impact evidence — each chain's form

```text
the OAuth chain:   the canary's access log: 'GET /?code=<the-auth-code>'
                   — the code reaching the canary is the impact
the SSRF chain:    the fetcher's response contains internal-host content
                   — the verbatim internal content
the bot chain:     the canary's access log: 'GET / ... User-Agent: <the-bot>'
                   — the bot's visit is the impact
the XSS chain:     the sink-value 'location.href="javascript:alert(1)"'
                   — the verbatim assignment + the browser's fire
the phishing chain: the canary's visit logged — the laundered-trust reach
```

## The partial-evidence traps

```text
'Location: evil.com'           <- RELATIVE — resolves to target.com/evil.com
                                  — NOT the cross-origin evidence; a
                                  same-origin redirect, NOT the gap
'Location: /dashboard'         <- a safe relative — a strong-negative
'Location: https://target.com' <- an allowlisted — a strong-negative
the meta reflects the param escaped <- a sanitized client-side twin
a javascript: the browser blocks   <- a client-side block, not a fire
```

## The evidence-record shape

```text
confirm: open-redirect
endpoint: /login  param: next  carrier: Location-header  status: 302
payload:  next=https%3A%2F%2Fattacker.invalid%2Flanding
evidence: 'Location: https://attacker.invalid/landing' (verbatim from --response)
```

## The chain-evidence record

```text
confirm: open-redirect -> oauth-code-launder
hop-1:   /login?next=... -> Location: https://evil.com (verbatim)
hop-2:   the OAuth redirect_uri -> Location: https://target.com/redirect?next=...
hop-3:   evil.com access log: 'GET /?code=<the-code>' (verbatim)
evidence-kind: impact
```
