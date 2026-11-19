# Detection — how to know an open-redirect surface is present

## The parameter signals — the destination names

```bash
# the redirect-parameter names — grep the source/bundle
grep -riE '(\?|&)(next|url|redir|redirect|redirect_uri|redirect_url|
return|returnTo|returnto|return_url|goto|dest|destination|target|
continue|out|view|callback|to|forward|link|ref|referer|site|host|
path|location|uri|redirect|checkOutUrl|CheckoutUrl|checkout_url|
success|successUrl|cancel|cancelUrl|fail|failUrl|error|errorUrl|
image|load|feed|host|port|domain|navigate|page|show|file|folder|dir|
doc|document|download|logout|login|signin|signout|auth|oauth|sso|
relay|RelayState|Relay|landing|ret|from|src|source|origin|back|prev|
previous|root|home|start|entry|exit|leave|away|offsite|external|ext|
outside|foreign|jump|hop|bridge|gateway|portal|via|through|via_url)=' "$BASE"
```

The vocabulary: `next`/`url`/`redir`/`redirect`/`redirect_uri`/`return`/
`returnTo`/`goto`/`dest`/`destination`/`target`/`continue`/`out`/`view`/
`callback`/`to`/`forward`/`link`/`ref`/`site`/`host`/`path`/`location`/
`uri`/`checkout`/`success`/`cancel`/`fail`/`error`/`image`/`load`/`feed`/
`port`/`navigate`/`page`/`file`/`doc`/`download`/`logout`/`login`/`signin`/
`signout`/`auth`/`oauth`/`sso`/`relay`/`RelayState`/`landing`/`ret`/`from`/
`back`/`prev`/`previous`/`root`/`home`/`start`/`exit`/`leave`/`away`/
`external`/`ext`/`outside`/`jump`/`hop`/`bridge`/`gateway`/`via`.

## The redirect-surface signals — the carriers

```bash
# the Location-header surface — the 3xx response
curl -sI "$BASE/login?next=/test" | grep -i '^location'
# the meta-refresh surface
curl -s "$BASE/x?url=y" | grep -iE 'meta.*refresh|http-equiv.*refresh'
# the JS-navigation surface
curl -s "$BASE/x?url=y" | grep -iE 'location\.(href|replace|assign)|window\.location|location\.hash'
```

## The first probe — the measurable oracle

```bash
# the canary — one external destination, follow=False
curl -i --max-time 10 "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding"
# read the Location: header — is it the canary?
# Location: https://attacker.invalid/landing  -> the oracle fires
# Location: /dashboard                        -> forced-relative (closed)
# Location: https://target.com/login          -> allowlisted (closed)
# 200 with a meta/JS redirect                 -> the client-side twin
```

```bash
# the tool — the param sweep + the boundary forms
python3 tools/web/redirect_probe.py --url "$BASE/login?next={CANARY}"
python3 tools/web/redirect_probe.py --url "$BASE/x" --param next
python3 tools/web/redirect_probe.py --selftest
```

## The auth-flow signals — the high-value params

- `redirect_uri`/`callback`/`return`/`returnTo`/`relay`/`RelayState` on an
  OAuth/SSO/SAML flow — the OAuth twin (`web-oauth-sso`)
- `next`/`continue`/`to`/`goto` on a login/logout/register flow — the
  post-auth landing
- `url`/`link`/`target`/`dest` on a link-shortener/outbound-click —
  the tracker-redirect
- `image`/`load`/`feed`/`src` on a fetch — the SSRF twin

## The detection-verdict ladder

- **surface** — the param exists, a `Location` returns — the redirect exists
- **candidate** — a `Location: <canary>` — the oracle
- **uniform** — a `Location: /`/`Location: <allowlisted>` on EVERY canary
  + bypass — the filter holds
- **weak-negative** — a `200`/no-`Location`/a `Location: <default>` on a
  guessed param — the param name was wrong
- **client-side** — a `meta`/JS redirect — the client-side twin

## The detection record

`detect: <endpoint>:<param>: <the signal>: <the confidence>` — the
param's name + the confidence; the oracle-verdict needs a `Location:`
carrying the canary verbatim.
