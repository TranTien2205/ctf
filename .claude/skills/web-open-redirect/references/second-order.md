# Second-order — the downstream surfaces the redirect opens

## The redirect's downstream effects — beyond the immediate launder

```text
a confirmed open-redirect is a PRIMITIVE — its second-order effects:
  - the Referer the victim's browser sends to the canary
  - the cookies/auth-state the victim carries to the redirect chain
  - the cached-redirect the CDN/proxy stores
  - the bot's state when it lands on the canary
  - the fragment the OAuth implicit-flow leaves
```

## Second-order — the Referer-leak

```text
the redirect lands the victim on evil.com; the victim's browser sends
Referer: https://target.com/login?next=... — the ORIGINATING URL — which
may carry a token/code/session-id in its query — a Referer-leak
```

```bash
# the canary's access log records the Referer
# GET / ... Referer: https://target.com/login?next=...&code=...
```

## Second-order — the cookie/auth-state carry

```text
the victim's browser follows the redirect — the cookies for evil.com are
sent (if any); a redirect to target.com.evil.com inherits the *.evil.com
cookies — a cookie-scope launder
```

## Second-order — the cached-redirect

```text
a 301/308 permanent redirect to evil.com may be CACHED by the CDN/proxy —
every subsequent visitor to the URL is redirected — a persistent launder
```

```bash
# check the cache-headers — a 301 with a Cache-Control is a persistent launder
curl -si "$BASE/login?next=//evil.com" | grep -iE 'cache-control|expires|location'
```

## Second-order — the bot's state

```text
the bot visits target.com/redirect?next=evil.com -> lands on evil.com ->
evil.com serves content the bot renders -> the bot's DOM-state/cookies/
localStorage on the attacker origin — a bot-state launder
```

## Second-order — the fragment-leak

```text
the OAuth implicit flow: Location: https://evil.com#access_token=<token>
the #access_token lands on the canary's origin — the canary's JS reads
location.hash -> the token — a fragment-carried token-leak
```

## Second-order — the history/back-button state

```text
the redirect's history-state — a back-button returns to the ORIGINATING
URL (the one with the redirect-param) — a re-nav loop; a `location.replace`
skips the history entry
```

## Second-order — the DNS/reputation carry

```text
the redirect borrows target.com's domain-reputation for the phishing —
the victim sees a "target.com" link and trusts it — a domain-reputation
launder
```

## Second-order — the multi-redirect chain

```text
a redirect to a second redirect to evil.com — the intermediate hops may
carry state (a token in a Referer, a cookie) — a chain of laundered-trust
```

## The second-order-record

`second-order: <the-effect>: <the-carrier>: <the-evidence>` — the
downstream effect's surface + the verbatim evidence.
