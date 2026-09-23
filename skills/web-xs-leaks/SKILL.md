---
name: web-xs-leaks
description: >
  Action-oriented depth skill for Cross-site leak / browser side channel. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-xss, web-cache-poisoning, web-csrf.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, xs-leaks, side-channel, browser, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# Cross-site leak / browser side channel

**Catalogue class.** This toolkit has never solved one. What follows is standard
published knowledge plus locally measured browser behaviour, not a local solve —
treat it as a starting point and record what actually happens in
`field-notes.md`.

## First probe

decide first where attacker code may run: if CSP or a URL allowlist keeps you from executing script on any origin the bot can reach, enumerate every piece of server state a plain GET from the bot can change, and use that as the read-back channel

**Falsifier** — the observation that closes this class: the bot can reach no attacker-influenced state at all, and no observable on the target changes as a function of what the victim's browser loaded

## Recognise

A bot visits a page with the victim's credentials, and you cannot read the
response. Two sub-shapes, and they need completely different plans:

| Shape | Where your JS runs | Read-back |
|---|---|---|
| **Classic** — bot visits a URL *you supply* | your own external origin | your own JS, directly |
| **Sealed** — bot visits a fixed URL on the target, CSP blocks script | nowhere | **server-side state only** |

The sealed shape is the hard one and it is now common. Tell them apart by
answering one question before any payload: *is there any origin, reachable by
the bot, on which I can execute one line of JavaScript?* A Chrome managed policy
(`URLBlocklist: ["*"]` with a one-entry `URLAllowlist`), or a challenge that
builds the visited URL itself, means no.

## Confirm

In the sealed shape the whole challenge is the read-back channel. Enumerate,
from source, **every mutation a plain GET from the victim's browser can cause**,
and check which of them you can observe afterwards as an unauthenticated user:

- **cache or store recency** — a store run with an LRU eviction policy
  (`--maxmemory-policy allkeys-lru`) turns every read into a write: a `GET` that
  touches a key refreshes it, so after you flood the store to force eviction,
  *the keys that survive are the ones the victim's browser fetched*. This is the
  highest-bandwidth channel available without script: thousands of bits per bot
  visit, not one.
- **a one-shot token** consumed by a GET (`GETDEL`, a single-use nonce) — one
  bit, and it burns your own ability to check.
- **a counter** you can read back by taking the next value.
- rate-limit buckets, quota counters, "last seen" timestamps.

Confirmation is a **control pair**: labels whose selector always matches and
labels whose selector never can. If the always-true and never-true labels do not
separate, the channel did not work and nothing downstream means anything.

## Operational probe

The declarative oracle, when no script is allowed. CSS attribute selectors read
a reflected value; each match fetches a distinct URL:

```css
body[secret^="ab"]{--m_ab:url('/paper/1234');}      /* prefix */
body[secret$="ef"]{--m_ef:url('/paper/1235');}      /* suffix */
body[secret*="abc"]{--m_abc:url('/paper/1236');}    /* substring */
#trig{background-image:var(--m_ab,none),var(--m_ef,none),var(--m_abc,none);width:1px;height:1px;}
```

Three things make this scale, all verified in Chrome on this machine:

1. **Custom property + one multi-layer `background-image`.** A matching rule can
   only set a variable; a single element then consumes thousands of them as
   background layers, and the browser fetches exactly the layers that resolved.
   Setting `background-image` directly in each rule does not work — only the
   last matching rule would win.
2. **Keep the reflected payload tiny.** Reflect
   `<link rel=stylesheet href='/paper/<id>'><div id=trig></div>` and put the
   thousands of rules in an uploaded stylesheet. Do not put the rules in the URL.
3. **`'unsafe-inline'` in `default-src` still allows styles** even when
   `script-src 'none'` blocks every script. Measured here: `script-src 'none'`
   blocks inline `<script>`, an SVG `<script>`, **and the XSLT stylesheet fetch
   itself** — XSLT is governed by `script-src`, so `<?xml-stylesheet?>` is not a
   CSP bypass. Without CSP the same XSLT runs and `document('/path')` will parse
   a `text/html` response as XML, which is worth remembering for targets whose
   CSP is weaker.

When the oracle only answers "does substring X occur", ask for **n-grams** —
all 1- and 2-char prefixes and suffixes plus every 3-gram — and reassemble the
value with a beam search over overlapping n-grams. Score each label as a
log-likelihood ratio calibrated from the control pair, never as a hard yes/no:
the eviction channel is noisy.

## Constraints that decide feasibility

Do this arithmetic **before** building anything:

- **How long does the secret live?** If it is `EX 60` and the verifying endpoint
  consumes it, the entire leak, the reconstruction and the submission must fit
  in that window, and you get exactly one guess.
- **What request rate do you need, and what do you have?** Measure it. Uploading
  a flood and probing thousands of markers inside a minute needs tens to hundreds
  of requests per second. If throughput is flat as you add workers, you are
  capped and the attack will not fit, however correct it is.
- `SameSite=Strict` does not protect a same-origin-only design: every request the
  bot makes to the target is same-site. It bites only in the classic shape, and
  a meta refresh issued *by the target* bypasses it.
- Reconstruction cost counts against the budget too. A beam search over big
  integer masks costs seconds per decode; vectorise it.

## Traps

- Do not assume "one bit per bot cycle". That is only true when the one-shot
  token is your channel. A recency or counter channel carries thousands.
- Controls are not optional. Without always-true and always-false labels you
  cannot tell a failed run from a wrong answer.
- A flood that forces eviction **destroys every other key in the store**. Only do
  it against an instance that is yours alone, and read the chain card's
  `blast_radius` first.
- The store's own keys are evictable too — if the secret lives in the same store
  you are flooding, you can delete the thing you are trying to read.
- A `GET` that both reads and consumes gives you one answer, ever. Spend it last.

## Routing

Shares signals with: `../web-xss/`, `../web-cache-poisoning/`, `../web-csrf/`.
Depth, one named file at a time: `../ctf-web/client-side.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
