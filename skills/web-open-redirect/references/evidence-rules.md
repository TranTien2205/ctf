# Evidence rules — what counts as proof of an open redirect

## The oracle — the verbatim Location

An open redirect is confirmed ONLY by a `Location:` response header carrying
the attacker-controlled destination. The verbatim header bytes are the
evidence — not the intent, not the probe that was sent.

```bash
# the probe
curl -si "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding"
# the evidence — the verbatim Location header
#   HTTP/1.1 302 Found
#   Location: https://attacker.invalid/landing   <- the canary, verbatim
```

The `Location: https://attacker.invalid/landing` — an absolute attacker URL
in the verbatim header — is the confirm. Record the full header + status.

## The evidence ladder

```text
surface    <- the param exists; a Location returns (the redirect exists)
candidate  <- Location: <the-canary> — the verbatim header carries it
impact     <- the chain fires — the OAuth code lands on the canary, the
              fetcher follows to the internal host, the bot visits it
```

A `candidate` (the `Location:` carrying the canary) is the class-confirm;
an `impact` (the chain firing) is the flag-path confirm. Both are
post-probe recordings — never claimed without the verbatim response.

## The post-probe record

```bash
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <id> --class web-open-redirect \
  --verdict confirms --evidence-kind class \
  --evidence 'Location: https://attacker.invalid/landing' \
  --response '<the verbatim 302 response>'
```

The `--evidence` must be a substring of `--response` — the gate checks.
`--evidence-kind class` for the `Location:` oracle; `--evidence-kind impact`
for the chain's downstream effect (the OAuth code reaching the canary).

## What is NOT evidence

```text
- the param "looks like" a redirect param — surface, not a confirm
- a 302 exists — surface; the Location's CONTENT is the evidence
- a `Location: /dashboard` — forced-relative — a NEGATIVE
- a `Location: https://target.com/safe` — allowlisted — a NEGATIVE
- a `javascript:` the browser BLOCKS — a client-side block, not a confirm
- "the client would follow it" — the CLIENT-side follow is not the
  server-side evidence; the Location header is
- a redirect the browser strips (a `//` it resolves same-origin) — read
  the verbatim header; the client may resolve differently than intended
- a meta/JS redirect — the client-side twin — the evidence is the
  meta-refresh content / the location.href value, not the absence of a
  Location header
```

## The verbatim-Location record shape

```text
confirm: open-redirect
endpoint: /login  param: next  carrier: Location-header
payload:  next=https%3A%2F%2Fattacker.invalid%2Flanding
evidence: 'Location: https://attacker.invalid/landing' (verbatim, from --response)
status:   302
```

## The client-side evidence — the meta/JS twin

```bash
# a meta-refresh — the content attribute carries the canary
curl -s "$BASE/x?url=https://attacker.invalid" | grep -i 'refresh'
# <meta http-equiv="refresh" content="0;url=https://attacker.invalid">
#   the 'content' value is the evidence

# a JS navigation — the assignment value
curl -s "$BASE/x?url=https://attacker.invalid" | grep -i 'location'
# <script>window.location="https://attacker.invalid"</script>
#   the assigned value is the evidence
```

The meta-refresh `content="0;url=<canary>"` and the `location="<canary>"`
are the client-side-twin evidence — record the verbatim attribute/assignment.

## The chain-impact evidence — the downstream effect

```text
the OAuth chain:   Location: https://target.com/redirect?next=... -> the
                   canary receives ?code=... — the code on the canary's
                   access log is the impact evidence
the SSRF chain:    the fetcher's response contains internal-host content
                   — the fetched content is the impact evidence
the bot chain:     the bot's visit logged on the canary — the referer/UA
                   is the impact evidence
```

## The record-discipline

- record the verbatim `Location:` — the bytes, not a description
- record the status (302/301/303/307/308) — the redirect type
- record the payload sent — the exact `next=` value
- record the client-side-twin evidence as the verbatim attribute/assignment
- record the chain-impact as the downstream observation (code-on-canary,
  fetched-content, bot-visit) — not "the chain would work"
- a negative is a record too — `Location: /` on every bypass = the filter
  holds = `negative-results.md`
