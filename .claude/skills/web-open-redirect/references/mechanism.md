# Mechanism — the gap the redirect produces

## The model

```text
[the client] --GET /login?next=X--> [the server] --302 Location:X--> [the client follows X]
                                        ^
                                        | the server controls where the
                                        | client is SENT next — if X is
                                        | attacker-controlled and unchecked,
                                        | the server launders the destination
```

The redirect is a server-issued `Location:` — the client's browser follows
it. A parameter inside the `Location` that names the destination — and is
not validated — is the open redirect. Alone it is low-value; the gap is
what it LAUNDERS.

## The four redirect carriers — where the destination lands

```text
1. the Location header     -> HTTP/1.1 302/301/303/307/308 Location:X
2. a meta refresh          -> <meta http-equiv="refresh" content="0;url=X">
3. a JS navigation         -> window.location=X / location.href=X /
                              location.replace(X) / location.assign(X)
4. a JS pushState/hash     -> history.pushState / location.hash=X
```

The server-side `Location` is the measurable oracle; the meta/JS are the
client-side twins — a `meta refresh` or `location.href` with the param
embedded is the same gap, client-side.

## The trust model — the param is the destination

```python
# the vuln shape — the param flows into the Location unchecked
@app.route('/login')
def login():
    next_url = request.args.get('next', '/')   # <- attacker-controlled
    # ... auth ...
    return redirect(next_url)                  # -> Location: <the param>
```

The vuln is the unchecked `redirect(next_url)` — the param reaches the
`Location` verbatim. The fix is an allowlist/relative-path force; the gap
is the missing/incorrect validation.

## The filter-gap taxonomy — the bypass surface

The server adds a filter — a check on the param — that fails on a
different parse than the browser's:

```text
filter:  startswith('/')         -> bypass: //evil.com (scheme-relative)
filter:  contains('target.com')  -> bypass: evil.com/target.com
filter:  endswith('target.com')  -> bypass: eviltarget.com (no dot-boundary)
filter:  startswith('https://')  -> bypass: https://target.com@evil.com
filter:  a regex on the param    -> a parse the regex does not match
filter:  a parser's host-read    -> a different parser's host-read
```

The filter checks ONE parse; the browser uses ANOTHER — the differential
is the bypass. `parser-differentials.md`/`filter-bypass-deep.md` are the
deep files.

## The chain value — what the redirect launders

```text
the redirect alone           -> a phishing URL (low)
the redirect -> an OAuth flow   -> a stolen code/token (web-oauth-sso)
the redirect -> a server fetch  -> an SSRF (web-ssrf)
the redirect -> a javascript:   -> an XSS (web-xss)
the redirect -> a bot visit     -> a bot-triggered action
the redirect -> a trusted-domain -> a domain-reputation laundering
```

The redirect's VALUE is the downstream trust — the class is rarely the
flag itself; it is the chain's first hop.

## The mechanism-to-skill map

| The gap | The flag-closing skill |
|---|---|
| the redirect -> an OAuth redirect_uri | `web-oauth-sso` |
| the redirect -> a server-side fetch | `web-ssrf` |
| the redirect -> a `javascript:`/`data:` | `web-xss` |
| the redirect -> a phishing/domain-launder | `web-info-disclosure`/the phishing shape |
| the redirect alone | `web-open-redirect` (the class) |

## The mechanism-record

`mechanism: <the param>: <the carrier>: <the filter-gap>: <the laundered
trust>` — the param is the destination; the carrier is the header/JS;
the filter-gap is the bypass; the laundered trust is the chain value.
