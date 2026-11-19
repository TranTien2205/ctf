# Per-falsifier — each falsifier's arms and the measured evidence

## Falsifier 1 — the forced-relative

```text
the falsifier: every canary + bypass -> Location: /<a-relative-path>
the arms tried:
  ?next=https://evil.com           -> Location: /
  ?next=//evil.com                 -> Location: /
  ?next=/\evil.com                 -> Location: /
  ?next=https://target.com@evil.com -> Location: /
  ?next=https://target.com.evil.com -> Location: /
  ?next=javascript:alert(1)        -> Location: /
the evidence: the verbatim 'Location: /' across every arm
the verdict:  the class falsifier fires — the destination is forced-relative
the reopen:   a different endpoint / a stored-redirect / a Referer-derived
```

## Falsifier 2 — the host-allowlist

```text
the falsifier: every arm -> Location: https://target.com/<safe-path>
the arms tried:
  ?next=https://evil.com           -> Location: https://target.com/
  ?next=https://evil.com@target.com -> Location: https://target.com/
  ?next=evil.com\@target.com       -> Location: https://target.com/
the evidence: the verbatim 'Location: https://target.com/...' across arms
the verdict:  the allowlist holds — the host is forced to target.com
the reopen:   an open-redirect ON target.com (the chain-hop) OR a
              subdomain-allowlist gap (x.target.com if *.target.com allowed)
```

## Falsifier 3 — the param-not-a-redirect

```text
the falsifier: the param produces NO Location/meta/JS carrier
the arms tried:
  ?next=evil.com -> 200 render (no Location)
  ?next=/x       -> 200 render
the evidence: no Location header in the response
the verdict:  a weak-negative — `next` isn't a redirect param on this
              endpoint; sweep the vocabulary
the reopen:   a different param name
```

## Falsifier 4 — the scheme-reject

```text
the falsifier: every scheme-arm is rejected
the arms tried:
  ?next=javascript:alert(1) -> 400 / Location: /
  ?next=data:text/html,...   -> 400 / Location: /
  ?next=file:///etc/passwd   -> 400 / Location: /
the verdict: the scheme-check holds — the scheme-surface is closed
the reopen: a `vbscript:`/`intent:`/`about:` alternative; a client-side
            sink (meta/JS) the server-side scheme-check doesn't cover
```

## Falsifier 5 — the client-side-twin sanitized

```text
the falsifier: the meta/JS value is escaped
the evidence:
  <meta content="0;url=/safe">        <- the meta sanitizes
  location.href="/safe"               <- the JS sanitizes
  location.href=escape(param)         <- escaped
the verdict: the client-side twin is closed
the reopen: a different sink / a DOM-source the sanitizer misses
```

## Falsifier 6 — the stored-redirect re-validated

```text
the falsifier: the stored param is re-checked at read-time
the evidence:
  /set-next?next=evil.com -> stored
  /login -> Location: /                <- the stored re-validated
the verdict: the stored-redirect is closed
```

## Falsifier 7 — the Referer-derived checked

```text
the falsifier: the Referer is validated or not-read
the evidence:
  GET /back  Referer: https://evil.com -> Location: /default
the verdict: the Referer-derived surface is closed
```

## Falsifier 8 — the chain-precondition dead

```text
the falsifier: the open-redirect confirms BUT the launder doesn't fire
the evidence:
  Location: https://evil.com          <- the class CONFIRMS
  + the OAuth allowlist strict + no allowlisted open-redirect
    -> the OAuth-chain is dead
  + the fetcher doesn't follow        -> the SSRF-chain is dead
the verdict: the class confirms; the chain is closed
```

## The falsifier-measurement record

```bash
# record each falsifier with the verbatim evidence
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict falsifies \
  --evidence 'Location: / on all arms (canary, //, \, %5c, @, subdomain, scheme)' \
  --response '<the verbatim safe Locations>'
```

## The falsifier-to-action map

| The falsifier | The next action |
|---|---|
| forced-relative | sweep a different endpoint / a stored/Referer surface |
| host-allowlist | find an open-redirect ON the allowlisted domain |
| param-not-a-redirect | the param-vocabulary sweep |
| scheme-reject | a `data:`/`vbscript:` alternative / a client-side sink |
| client-side-twin sanitized | a different sink |
| stored re-validated | a different flow |
| Referer checked | a different surface |
| chain-precondition dead | a different laundered-trust |
