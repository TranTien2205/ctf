# Falsifiers — the observations that close this class

## The class falsifier (from the class contract)

> **the destination is validated against an allowlist or forced to a
> relative path** — send every canary + bypass; if the `Location:` is
> always a safe relative path or an allowlisted host, the class is closed.

```bash
curl -si "$BASE/login?next=https%3A%2F%2Fevil.com" | grep -i '^location'
curl -si "$BASE/login?next=%2f%2fevil.com" | grep -i '^location'
curl -si "$BASE/login?next=%5c%5cevil.com" | grep -i '^location'
# Location: /  or  Location: https://target.com/safe  on EVERY form
#   -> the allowlist/relative-force holds -> the class falsifier fires
```

## The per-mechanism falsifiers

| The mechanism | The falsifier — what closes it |
|---|---|
| an unchecked `Location` | every canary → `Location: /` or an allowlisted host |
| a `//host` scheme-relative bypass | `//evil.com` → `Location: /` or a normalized rejection |
| a prefix-filter bypass | `//evil.com`/`https://target.com.evil.com` → allowlisted or rejected |
| a substring-filter bypass | `evil.com/target.com` → allowlisted or rejected |
| a parser-differential | `evil.com\@target.com`/`%5c`/`%40` → all normalized to safe |
| an OAuth-redirect chain | the `redirect_uri` is strictly allowlisted AND no open-redirect on the allowlisted domain |
| an SSRF-chain | the fetcher doesn't follow `Location`, OR the redirect is allowlist-checked |
| a `javascript:`/`data:` scheme | the scheme is rejected/normalized to `http(s)` |
| a client-side meta/JS redirect | the value is escaped/sanitized; the param doesn't reach the sink |
| a Referer-derived redirect | the Referer isn't read / is allowlist-checked |
| a stored-redirect | the stored `next` is validated when read |
| a CRLF injection | `%0d%0a` is stripped/rejected — no header split |

## The uniform-response falsifier

```text
every canary + bypass arm -> Location: /login  (a fixed safe default)
                          -> Location: https://target.com/dashboard
                          -> 400 Bad Request (the param rejected)
                          -> a Location the canary is NOT in
```

A uniform safe response across every arm is the class's mechanism-level
falsifier — the validation holds regardless of the parser boundary.

## The "param is not a redirect" falsifier

```text
the param exists but the response has NO Location / no meta-refresh /
no JS-navigation -> the param isn't a redirect param — a weak-negative;
the param name was wrong, OR the redirect fires on a different flow
```

## The "client-side only, and sanitized" falsifier

```text
the param reaches a meta-refresh/location.href BUT the value is
escaped/sanitized -> the client-side twin is closed
<a href="/x?url=https%3A%2F%2Fevil.com">  <- reflected escaped, not a redirect
window.location = sanitize(url)           <- sanitized
```

## The "the allowlist is on a subdomain I can't reach" falsifier

```text
the OAuth allowlist is target.com, and target.com HAS an open redirect,
BUT the redirect_uri check requires an exact subdomain I can't control
-> the chain is closed for that allowlist
```

## The "impact doesn't launder" falsifier

```text
the open-redirect confirms (Location: evil.com) BUT:
  - the OAuth code isn't in a GET param (fragment-only + the fragment
    doesn't survive) -> the token doesn't reach the canary
  - the fetcher doesn't follow redirects -> the SSRF chain is dead
  - the bot visits the URL but the redirect is client-side and the bot
    doesn't execute JS -> the bot chain is dead
```

A confirmed open-redirect can still fail to LAUNDER — the chain's
precondition is separately falsifiable.

## The falsifier-to-ledger record

```bash
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <id> --class web-open-redirect \
  --verdict falsifies \
  --evidence 'Location: / on canary + //evil.com + %5cevil.com + userinfo' \
  --response '<the verbatim safe responses>'
```

A falsifier is a MEASURED observation — the verbatim safe `Location`s across
every bypass arm — not "it didn't work". Record the arms tried.

## The falsifier table

| The observation | The verdict |
|---|---|
| `Location: /`/`allowlisted` on all arms | the class falsifier fires |
| no `Location`/meta/JS on the param | the param isn't a redirect (weak-negative) |
| the client-side twin is escaped | the client-side twin is closed |
| the chain precondition fails | the open-redirect confirms but doesn't launder |
| the meta-refresh carries `javascript:` but browsers block it | a client-side block, not a confirm |
