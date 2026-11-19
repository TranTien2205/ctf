# Case studies — the solved patterns this skill is built from

## apexsurvive — local bot debugging for a stored-XSS chain

The verified anchor. The challenge carried a multi-stage client-side
chain — a stored XSS that had to fire inside the admin bot's browser
and reach a template-overwrite RCE.

**The lesson:** payload development happened against a local headless
browser, and only the confirmed payload was fired at the real bot.

- the live bot was a blind channel — a handful of visits, no error
  output
- the local reproduction turned each payload iteration into a normal
  debug loop with console and network visible
- the payload was iterated until it fired cleanly locally
- only then was it fired at the live bot — once, and it worked

**Transfer:** when a challenge gives you a bot and a client-side
payload path, the first hour is building the local reproduction, not
firing guesses. The bot's source (when supplied) is the spec — copy
its URL, credential, wait, and flags exactly.

## tornadoservice — the tunnel interstitial

The recorded failure that motivates the reachability pre-check. The
payload's exfil channel was a tunnel (a public URL forwarded to the
local listener) — and the tunnel inserted an interstitial/confirmation
page that a headless browser could not pass.

**The lesson:** attempts were lost to a channel that looked correct —
the URL was right, the listener was up — but the headless client never
reached the listener through the interstitial.

- a fetch to `https://tunnel/...` from inside a headless browser hits
  a "click to continue" page instead of your listener
- the fix is to *check the channel first*: fetch your own tunnel URL
  from inside the driver and read what actually loads
- only a tunnel that returns your real body — no interstitial — is a
  usable channel

**Transfer:** before spending a bot visit, prove a headless client can
reach your exfil endpoint. `page.goto(your_url)` then `page.content()`
— if it is not your body, the channel is dead for headless, and the
payload is dead with it.

## The combined pattern

Both cases point at the same workflow:

```
reproduce -> develop locally -> verify the channel -> fire once
```

The skill exists because the blind channel is the expensive path — a
bot visit is worth a hundred local iterations.
