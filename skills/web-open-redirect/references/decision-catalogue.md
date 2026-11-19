# Decision catalogue — every decision the operator makes, catalogued

## Decision 1 — is this param a redirect?

```text
the probe: ?<param>=https://attacker.invalid -> curl -si | grep -i location
the verdicts:
  Location: <the-param>          -> YES — a redirect param; continue
  Location: <a fixed page>       -> the param exists but isn't read — weak-neg
  no Location / a 200 render     -> NO — not a redirect param — next name
  a 400/422                      -> a format-reject — the relative-form check
```

## Decision 2 — what carrier?

```text
the response carries:
  Location: header   -> the server-side redirect — the canonical
  Refresh: header    -> a non-Location header — a client-side carrier
  <meta refresh>     -> the client-side tag
  location.*         -> the client-side JS-sink
  nothing            -> the param isn't a redirect — a different name
```

## Decision 3 — what's the filter? (the fingerprint)

```text
Location: <canary>          -> NO FILTER — the CANDIDATE
Location: /                 -> a forced-relative — the //, /\, %5c arms
Location: <allowlisted>     -> a host-allowlist — the @, \@, subdomain arms
Location: <partial>         -> a path/host-force — the suffix/substring arms
```

## Decision 4 — which arm?

```text
the filter-shape -> the arm:
  startswith('/')      -> //evil.com, /\evil.com, \\evil.com
  startswith('/') && !// -> /\evil.com, /%5cevil.com, /\/evil.com
  contains('t.com')    -> evil.com/t.com, t.com.evil.com, eviltarget.com
  endswith('t.com')    -> eviltarget.com, x.target.com (subdomain)
  hostname/netloc      -> the userinfo, the \@, the encoded-host
  scheme-check         -> https:evil.com, javascript:, data:
  decode-check         -> the encoded, the double-encoded
  a hardened residual  -> the evasion.md arms
```

## Decision 5 — is the class closed?

```text
a uniform Location: <safe> on EVERY canary + bypass arm -> the class
falsifier fires — the destination is validated/forced — close the surface
```

## Decision 6 — is there a chain?

```text
the confirmed Location: <canary> + the laundered-trust:
  on an allowlisted redirect_uri domain -> the OAuth chain
  + a fetcher that follows              -> the SSRF chain
  + a javascript:/data: sink            -> the XSS chain
  + a bot that visits                   -> the bot chain
  + the phishing shape                  -> the standalone answer
```

## Decision 7 — what's the verdict?

```text
a Location: <canary>         -> confirms --evidence-kind class
a Location: <safe> on one arm -> negative — that arm blocked
a Location: <safe> on all arms -> falsifies — the class closed
no Location on a guessed param -> negative (weak) — the name is wrong
the chain's downstream fires   -> confirms --evidence-kind impact
```

## The decision-record

`decision: <the-question>: <the-observation> -> <the-action>`
