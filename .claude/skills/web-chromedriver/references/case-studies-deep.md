# Case studies deep — the anchors, analysed

## apexsurvive — the anatomy of local-bot development

**The challenge shape**: a multi-stage client-side chain — a stored
XSS that had to fire in the admin bot's browser and reach a template-
overwrite RCE.

**What the local bot bought**: the payload had several stages (inject,
read, exfil, chain) — each needed to fire correctly in sequence inside
a real renderer. Against the live bot, a failure at any stage is a
silent dead visit. Against the local bot, each stage's console/error/
network was visible, so the payload was iterated stage by stage until
the whole chain ran clean.

**The specific transfer points**:

- the bot's source named its URL, cookie, wait, and flags — the
  reproduction copied each, so local confirmations transferred
- the staged-marker technique (`S1`/`S2`/`S3` console logs) located
  which stage died on each iteration
- the exfil channel was verified from inside the driver before the
  live fire
- the confirmed payload was fired at the live bot **once** — and
  worked, because it had already been proven in the reproduction

**The lesson generalised**: when a challenge gives you a bot and a
client-side payload path, the *first* hour is the reproduction, not
the payload. The blind channel is the expensive path; the local loop
is the cheap one, and it is the only one that shows you the failure.

## tornadoservice — the interstitial anatomy

**The challenge shape**: a payload whose exfil channel was a public
tunnel to the local listener.

**What went wrong**: the tunnel (a free tier) inserted a "click to
continue" interstitial in front of the forwarded URL. A normal browser
user clicks through it; a headless browser never does — the payload's
`fetch` to the tunnel URL received the interstitial HTML, not the
listener. Attempts were spent on a payload that was correct but whose
*channel* was dead for headless.

**The specific transfer points**:

- a `fetch`/`goto` to your own tunnel from inside the driver reveals
  the interstitial immediately — `page.content()` shows the confirm
  HTML, not your body
- the check costs seconds and must run *before* the first live fire
- a tunnel without a confirm page, a raw TCP listener + port-forward,
  or a same-origin channel all resolve it

**The lesson generalised**: the exfil channel is part of the payload.
Verify a headless client can reach it *from inside the driver* before
spending a bot visit — `tornadoservice` is the recorded cost of
skipping that check.

## The combined anatomy

Both cases are the same workflow seen from its two failure modes:

```
apexsurvive:     reproduce -> develop locally -> fire once
tornadoservice:  ... verify the channel ->     ... or lose the visits
```

The first is the discipline working; the second is the discipline's
most-skipped step. Together they define the skill: the local
reproduction makes the payload debuggable, and the channel check makes
the live fire count.
