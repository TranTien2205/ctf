# PhantomFeed — HackTheBox University CTF 2023 (web, hard)

Flag: recorded in `challenges/phantomfeed/state.json` via `tools/hooks.py pre-flag`
(live response, `GET /backend/static/zz.txt`).
Assistance: writeup-assisted. White-box reading found the sink, the bot, the
unvalidated `redirect_url` and the ReDoS. `tools/writeup_search.py` supplied the
two pieces local evidence could not: the Nuxt client-side open redirect, and the
fact that the race is won by volume rather than by timing.

## Layout

One container, nginx on 1337 in front of three services:

| Path | Port | Service |
|---|---|---|
| `/` | 5000 | Nuxt 2.15.7 SPA (phantom-market-frontend) |
| `/phantomfeed` | 3000 | Flask auth server + social feed |
| `/backend` | 4000 | Flask market API |

`entrypoint.sh` renames the flag to `/flag<10 hex>.txt` and generates an RSA pair
at `/app/private.pem` / `/app/public.pem`. Only phantom-feed holds the private
key; the market backend verifies RS256 with the public key. `WORKDIR /app`, so
both Flask apps open the same `sqlite:///storage.db`.

## Sink

`phantom-market-backend/application/blueprints/routes.py:90` — `POST
/backend/orders/html`, `adminMiddleware`, `color` from the form:

```py
orders_template = render_template("orders.html", color=color)
pdf = html2pdf.convert(orders_template, orders)
```

`templates/orders.html` is `<para><font color="{{ color }}">Orders:</font></para>`
and `util/document.py:13` does `Paragraph(text)`. reportlab is pinned at
`3.6.12`, so the colour attribute is evaluated — **CVE-2023-33733**.

Jinja escapes the payload's `'` and `<` to `&#39;` and `&lt;`, and reportlab's
own parser decodes character references inside the attribute before evaluating,
so the payload survives unchanged. No encoding work is needed.

The gate is an `administrator` RS256 JWT, and `create_jwt` sets
`user_type: "administrator"` only when `username == "administrator"`. The
administrator row is seeded in `migrate()` with a 32-byte random password, so
the token has to come out of the bot.

## 1. ReDoS turns email verification into a race

`send_email` is `pass`, so a verification code is never delivered and a fresh
account can never log in. But `register` runs in this order:

```py
user_valid, user_id = db_session.create_user(username, password, email)  # verified defaults True
email_client = EmailClient(email)                                        # parse_email runs here
verification_code = db_session.add_verification(user_id)                 # sets verified False
```

`parse_email`'s regex, `^([0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*@...)$`, has two
nested quantifiers over overlapping character classes. `a@` + 26 `a` + `!`
backtracks exponentially: measured on the target, 24 characters took 2.75s, 27
took 10.46s and 28 took 18.2s, against a 1.31s baseline.

The window is real but **not reachable by timing a single request**. Measured:
nine logins sent between t+0.3s and t+13s of an 18.2s window all returned at
t+18.2s with 401 — the regex holds the GIL, so a request costing as much Python
as a login (SQLAlchemy `create_all`, bcrypt, an RSA signature) makes no progress
at all and is served only once the regex ends, by which time `add_verification`
has committed. A cheap GET is served during the window; a login is not.

What wins is volume: **100 logins fired concurrently with the register**. They
all unblock together when the regex ends, and one of them reads the row before
the register thread's UPDATE commits. One run, first try.

Raising the window instead does not help: nginx's `proxy_read_timeout` is 60s,
so a 30-character payload returns 504 for both requests.

## 2. Nuxt client-side open redirect

`bot_runner` sets an `administrator` JWT cookie on domain `127.0.0.1` — no port,
so it is sent to 1337, 3000, 4000 and 5000 alike — and then visits

```py
client.get("http://127.0.0.1:5000" + link)
```

with `link` taken straight from a post's `market_link`. A `link` beginning
`///host` makes the path `///127.0.0.1:1337/...`, which Nuxt 2.15.7's client
router resolves as protocol-relative and navigates to (nuxt/nuxt#10319).

This is client-side only: requesting `///127.0.0.1:1337/probe` through nginx
returns 200 with no `Location` header. The redirect was confirmed instead with
an in-band oracle — mint an authorization code, send the bot at the token
endpoint with it, and check whether the code is still redeemable. It was not,
so the bot had reached the endpoint.

## 3. The token endpoint is the XSS

`/phantomfeed/oauth2/token` returns a bare `str`, so Flask serves it as
`text/html`, and `redirect_url` is reflected into it verbatim next to the token:

```
{"access_token": "eyJ...", "token_type": "JWT", "expires_in": 1800, "redirect_url": "<script>…</script>"}
```

`generate_authorization_code` binds only `client_id` and `redirect_url`, never a
user, and `/oauth2/token` mints the token for whoever holds the cookie. So the
code is minted with our own session, with `redirect_url` set to the script, and
the bot is sent to redeem it — the bot's own administrator token lands in a page
running our script.

`json.dumps` escapes `"` and `\`, so the payload contains neither;
`String.fromCharCode(34)` supplies the quote used to split the JSON.

Exfiltration is in-band, with no external listener: the script posts the token
back to `/phantomfeed/feed`, which the bot may do because its cookie is
same-site for its own origin.

```js
<script>fetch('/phantomfeed/feed',{method:'POST',credentials:'include',
headers:{'Content-Type':'application/x-www-form-urlencoded'},
body:'market_link=/zz&content=TK'+document.body.innerText.split(String.fromCharCode(34))[3]})</script>
```

## 4. RCE

With the administrator access token, place one order (the route returns early
when there are none), then send the colour payload with
`cp /fl*.txt /app/phantom-market-backend/application/static/zz.txt` — a glob,
because the flag's name is randomised. `static` is registered on the Flask app
rather than the blueprint, so `@web.before_request` does not guard it and
`GET /backend/static/zz.txt` is readable without a token.

## Traps that cost time

* The verification race cannot be timed. Nine staggered logins lost; 100
  simultaneous ones won. The regex starves anything expensive.
* A longer ReDoS payload is worse, not better: nginx returns 504 at 60s.
* The Nuxt open redirect leaves no server-side trace. Test it with the
  authorization code's own consumption, not with a `Location` header.
* A first exfil attempt looked like a failure and was not: the detector expected
  no digits between `access_token` and the JWT, but Jinja renders the quotes as
  `&#34;`, which contains digits.
* `market_link` must be non-empty, and each post blocks the request for the
  whole bot run (measured 38s), so fire it on a thread and poll the feed.

## Cleanup

`/app/phantom-market-backend/application/static/zz.txt` was removed with a
second colour payload and now returns 404. The race accounts, the feed posts
(one of which holds the leaked administrator token) and the placed order remain
in the instance's SQLite database; there is no delete route, and rewriting rows
in a database shared by both services was not worth the blast radius.
