# Summary — the CSRF mental model in one page

## The class

Make a browser send a state-changing request the victim didn't
intend, under ambient credentials — a cookie, a network position,
or a shared jar.

## The proof

A CSRF is a DELIVERY primitive — the proof is the state change read
back separately, never the request's HTTP status or the delivery's
reach.

## The six gates

```
1. does the write exist?              → a state-changing endpoint
2. does the viewer exist?             → a bot/victim/stored-context
3. does the credential attach?        → SameSite read
4. is a token required+verified?      → the strip test
5. is Origin/Referer enforced?        → the foreign/absent replay
6. can a form produce the body?       → the content-type test
```

## The carriers

```
urlencoded form POST   → field-based writes
text/plain form POST   → JSON via the =-absorption
multipart form         → file/field writes
GET top-nav            → Lax-safe GET writes
fetch no-cors          → fire-and-forget
sendBeacon             → unload-safe
iframe/sub-resource    → None-cookie GETs
data:/stored/subdomain → the same-site/bypass contexts
```

## The two card shapes

```
TornadoService: localhost gate + bot → the bot IS the local client
                → a form-nav to 127.0.0.1 passes the remote_ip check
SSOS: shared jar + login → the CSRF'd Set-Cookie swaps the jar's
      token to your account → the bot writes the flag to you
```

## The falsifier

```
a token the page can't read AND session-bound, OR a Strict cookie
with no same-site vector, OR an enforced Origin with no bypass, OR
a json-only content-type + strict — and no stored-content path.
then the class is closed; record refutes and pivot.
```

## The escalation

```
when every gate is measured and the delivery still fails → name the
gate that held → pivot to the class that bypasses it:
- token/stored → XSS
- a read → CORS
- a server-fetch → SSRF
- a side-channel → XS-leaks
- a ws channel → web-websocket
```

## The files

```
workflow / field-manual / cheatsheet        → the procedure
verified-chains                              → the two cards
samesite-matrix / cookie-attributes-deep     → the cookie gates
token-defenses / token-bypass-deep           → the token gate
origin-referer / headers-deep                → the header gates
content-type-gate / content-type-carriers    → the body gate
delivery-* / json-body-assembly / payload-*  → the carriers
bot-* / pna-and-loopback / websocket-csrf    → the viewers
login-csrf / oauth-sso-csrf / stored-*       → the write-types
readback-oracles / evidence-rules            → the proof
troubleshoot / delivery-troubleshoot         → the failures
case-studies / exploitation-playbook         → the worked shapes
framework-matrix / frameworks-deep           → the per-stack
theory / class-boundary / glossary           → the model
```
