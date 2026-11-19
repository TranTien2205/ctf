# Edge cases deep — the states that break the simple model, in detail

## The bot's session is pre-authenticated

Some bots authenticate before visiting — a login `fetch`, a session
cookie set from the app's own auth flow. The page your payload sees is
the *post-auth* view, which may render different DOM/context than the
anonymous page you tested on. Reproduce the auth step:

```python
# if the bot logs in first, do the same
page.goto('http://app/login')
page.fill('#user','admin'); page.fill('#pass','x'); page.click('#go')
# now the session is the bot's — THEN goto your URL
page.goto(your_url)
```

A payload tested on the anonymous page may land in a context the
bot's authenticated page never produces.

## The flag cookie is SameSite=Strict

`SameSite=Strict` cookies are dropped on cross-origin navigations —
a bot that reaches your payload page via a redirect or an external
link may not carry the flag cookie to it. The payload then has no
cookie to exfil. Reproduce the navigation path — if the bot visits
your URL *directly* (not via a cross-site link), the cookie is sent;
if via a link, it may not be.

## The payload lives across a navigation

A bot that navigates your URL then immediately navigates elsewhere
destroys your payload's context mid-execution. A payload that needs
two pages of work (read flag on page A, exfil on page B) dies at the
navigation. Fix: a fire-and-forget exfil (`sendBeacon`, `Image`) that
survives, or a same-origin write completed before navigation.

## The driver is on a different host than the app

A Grid node or a remote driver may run in a *different container* than
the app — its `localhost` is the node's, not the app's. The `file://`
read hits the node's filesystem; `localhost` reaches the node's
services. Reproduce the *network topology*, not just the flags — the
reads land wherever the browser process lives.

## The endpoint serialises sessions

A single-driver endpoint or a busy Grid may allow only one session at
a time — your `POST /session` queues or fails while another is active.
On a shared instance, another team's leaked session can hold the
slot. `GET /sessions` + a cleanup, or a capability that opens a
second browser, resolves it.

## The file is binary or huge

A `file://` read of a binary renders as mojibake or downloads instead
of rendering; a huge file can hang the `source` serialisation. The
read path for binary: `execute` `fetch("file://")` -> `arrayBuffer`
-> base64 inside the page -> read the string. For huge files, read a
known small file first to prove the primitive, then target the flag
path directly rather than a directory walk.

## The bot runs with a disabled-web-security flag

`--disable-web-security` removes the same-origin policy — the bot's
browser can read any origin. Reproduce it only if the bot actually
sets it; a payload that relies on cross-origin reads works locally
with the flag and dies live without it. It is a reproduction axis,
not a default.

## The challenge pins a WebDriver behaviour

Some challenges build the bot on a specific driver behaviour — a
particular `execute` return shape, a known WebDriver quirk. Reproduce
the same *driver version* when the behaviour is the point — a
chromedriver of a different vintage may serialise differently.
