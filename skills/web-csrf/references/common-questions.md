# Common questions — the CSRF FAQ

## "The endpoint returned 200 — did the CSRF work?"

No — the 200 says the REQUEST reached the server. The write's
proof is the state change read back separately — the marker on your
object, the delta on a balance, the record in a list.

## "The cookie is HttpOnly — can I still CSRF?"

Yes — HttpOnly blocks JS from READING the cookie, not the browser
from ATTACHING it. A CSRF needs the cookie attached, not read.
HttpOnly is irrelevant to the attach (it matters only if you need
to read the cookie's value — a double-submit you must echo).

## "SameSite=Lax — is the CSRF dead?"

Only for POST/sub-resource — Lax still attaches on a top-level GET
navigation. A GET-reachable write survives Lax via a form GET, a
link, a `location=`, a meta-refresh. A POST-only write is dead via
this cookie — needs a different credential or a stored page.

## "The endpoint needs a token — game over?"

Not yet — check whether it's VERIFIED. Strip it, send empty, replay
your own token under a different session, check if it's session-
bound, check if it's readable cross-origin (a CORS-open endpoint,
a leak). A token that's decorative, replayable, or readable is a
bypass.

## "The Origin check exists — is it enforced?"

Measure it — a foreign-Origin replay. If the endpoint answers the
same as same-origin, the header is decorative. If it 403s, check
the bypass shapes: absent-Origin (a data:/no-referrer page), `Origin:
null`, a substring-host match, a trusted subdomain.

## "The endpoint wants JSON — a form can't send application/json."

Right — but ship it as `text/plain` (a form enctype the browser
allows) and check if the server parses the body regardless of the
declared type. The `=`-absorption trick makes the form's body valid
JSON. If the server whitelists content-type strictly, it's dead via
form — a sibling urlencoded route is the remaining shape.

## "The bot visited but nothing changed — did it fail?"

Inconclusive — could be a slow oracle, a partial write, a missed
field, or a gate that held silently. Poll the oracle longer, then
check which gate held — the cookie didn't attach, the write didn't
reach, or the bind dropped the field.

## "Can I read the CSRF's response?"

No — `no-cors`/form navs make the response opaque. If you need the
response (a token, the flag), the write must store it somewhere you
read separately, OR the endpoint must be CORS-open (then it's a
read, the `web-cors` class).

## "The bot's on https but the target is http — the form won't fire."

Mixed content — an https page can't POST to http. Host the CSRF
page on http, or use a `data:` page, or a same-scheme target.

## "A fetch to 127.0.0.1 got blocked — Private Network Access."

Chrome's PNA preflights private-network fetches from public contexts.
A FORM NAVIGATION isn't PNA-gated the same way — use a form, not a
fetch, for loopback targets (the card's shape).

## "The token is double-submit — a cookie must match the form."

Plant the cookie yourself — a subdomain cookie-set, a header-
injection, a cookie-bomb — then the form's value matches the planted
cookie. The check is `cookie==form`, not `token==session`.

## "The write is on a GET — is that still CSRF?"

Yes — and it's the Lax-open case. A GET-with-side-effect is CSRF-
able even under SameSite=Lax via a top-level navigation. The most-
missed shape.

## "There's no token at all — is it automatically vulnerable?"

No — a missing token is ONE missing gate. SameSite=Strict, an
enforced Origin/Referer, or a required content-type may still close
it. Measure ALL the gates, not just the token.

## "The bot's cookie jar — does it persist across visits?"

The SSOS shape needs it. A fresh-incognito-per-visit bot loses
cookies between cycles; a persistent-profile bot keeps them. Check
the bot's launch config (`userDataDir`, a persistent profile).
