# Negative results (deep) — the full negative taxonomy

## The negative-ladder

```text
weak-negative    <- a null/no-Location on a guessed param — the name is
                    wrong; NOT a class verdict
strong-negative  <- a verbatim Location: <safe> on a real redirect param
                    — the param IS a redirect but validated — a class verdict
uniform          <- Location: <safe> on EVERY arm — the filter holds —
                    the class falsifier
carrier-negative <- a meta/JS sink that's escaped/sanitized — the client-
                    side twin is closed
chain-negative   <- the open-redirect CONFIRMS but the launder doesn't fire
```

## The weak-negative taxonomy — the wrong-param guesses

| The guess | The response | The read |
|---|---|---|
| `?next=evil.com` | `200 render` | `next` isn't the param |
| `?url=evil.com` | `400` | `url` rejected outright |
| `?redir=evil.com` | `Location: /dashboard` | a fixed-safe — `redir` isn't it |
| `?return=evil.com` | `200 render` | `return` isn't the param |
| `?callback=evil.com` | `404` | no `callback` param |
| `?to=evil.com` | `200` | not a redirect param |

## The strong-negative taxonomy — the measured validation

| The arm | The Location | The read |
|---|---|---|
| `https://evil.com` | `Location: /` | external host blocked |
| `//evil.com` | `Location: /` | scheme-relative blocked |
| `/\evil.com` | `Location: /` | backslash normalized |
| `\\evil.com` | `Location: /` | UNC normalized |
| `https://target.com@evil.com` | `Location: /` | userinfo rejected |
| `evil.com\@target.com` | `Location: /` | `\@` normalized |
| `https://target.com.evil.com` | `Location: /` | subdomain rejected |
| `javascript:...` | `400`/`Location: /` | scheme rejected |
| `%252f%252fevil.com` | `Location: /` | double-encode normalized |

## The uniform-negative — the class-closing

```text
all arms -> Location: <the-same-safe>
the arms-tried list IS the falsifier's evidence — record each arm +
each verbatim safe Location
```

## The carrier-negative — the client-side twin closed

```text
?url=https://evil.com -> <meta content="0;url=/safe">        <- meta sanitizes
?url=https://evil.com -> location.href="/safe"               <- JS sanitizes
?url=https://evil.com -> <a href="/x?url=...">                <- reflected, not nav
?url=https://evil.com -> window.location=escape(url)         <- escaped
?url=javascript:...    -> location.href="about:blank"         <- the scheme normalized
```

## The chain-negative — the confirm that doesn't launder

```text
the open-redirect CONFIRMS:  Location: https://evil.com
the chain-negative:
  - the OAuth redirect_uri is strict AND the allowlisted domains have no
    open-redirect   -> the OAuth-chain is dead
  - the fetcher doesn't follow redirects -> the SSRF-chain is dead
  - the javascript:/data: is blocked    -> the XSS-chain is dead
  - the bot doesn't run JS / a meta     -> the bot-chain is dead
  - the redirect resolves same-origin   -> the launder is dead
```

## The partial-negative — the fingerprint's failure-modes

| The fingerprint | The partial-negative read |
|---|---|
| `Location: /` on `https://evil.com` but `Location: //evil.com` on the `//` | the host-block holds but the `//` passes — the PARTIAL is the mechanism fingerprint |
| `Location: https://target.com/x` on `https://evil.com` | a host-force — the `@`/substring arms are the residual |
| `Location: /` on `//evil.com` but a `Location: /\evil.com` on `/\evil.com` | the `//`-block holds but `/\` passes — the fingerprint names the filter |

## The different-surface negative — the class is closed HERE not THERE

```text
/login?next=<all arms> -> Location: /   <- /login is closed
BUT /logout?next= /error?next= /out?url= /back<-Referer — the unswept
surfaces — the falsifier closes THE SWEPT SURFACE only
```

## The weak-vs-strong distinction — the operational rule

```text
weak-negative:   "no signal" — the param wasn't a redirect; keep sweeping
strong-negative: "the Location was safe" — the param IS a redirect but
                 validated; record the arm
uniform:         "every Location was safe" — the class falsifier; record
                 the arms-tried + close the surface
```

## The negative-record

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict negative \
  --evidence 'Location: / on https://evil.com and //evil.com and /\evil.com' \
  --response '<the verbatim safe Locations>'
```

## The negative-to-reopen map

| The negative | The reopen precondition |
|---|---|
| `/login` closed | `/logout`/`/error`/`/out`/`/goto` unswept |
| the param closed | a different param name |
| the param closed | a different carrier (Referer/stored/meta/JS) |
| the `//` blocked | `/\`/`\\`/`%5c`/`%2f` |
| the `@` blocked | `\@`/encoded-`@`/query-`@` |
| the OAuth-chain dead | a different allowlisted domain's open-redirect |
| the SSRF-chain dead | a different fetcher that DOES follow |
