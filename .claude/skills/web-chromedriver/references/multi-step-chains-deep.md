# Multi-step chains deep — the staged exploit shapes, expanded

## The reproduction -> exfil chain (the canonical one)

```
STAGE 1: the injection (web-xss)
   a stored/reflected payload the admin bot renders
   -> owned by ../web-xss/

STAGE 2: the reproduction (web-chromedriver)
   local bot matching the challenge's bot on URL/cookie/wait/flags/version
   -> confirmed the payload fires in the reproduction

STAGE 3: the exfil (web-chromedriver)
   the payload carries the flag off the page — fetch/Image/beacon/write-back
   -> confirmed the exfil leaves in the reproduction

STAGE 4: the live fire (web-chromedriver)
   fire once at the real bot -> the listener captures the value

STAGE 5: the gate
   tools/hooks.py pre-flag the flag-shaped string
```

The browser harness owns stages 2–4 — the reproduction and the exfil —
while the injection class owns stage 1.

## The apexsurvive chain (the multi-class one)

```
STAGE 1: stored XSS payload (web-xss)
STAGE 2: local-bot development -> confirmed each stage (web-chromedriver)
STAGE 3: payload exfils the bot's credential/token (web-chromedriver)
STAGE 4: replay the credential -> reach a template-write primitive
STAGE 5: template overwrite -> RCE (web-ssti / web-command-injection)
STAGE 6: the flag -> pre-flag
```

The harness is the *connector* — it confirmed the XSS stage locally
before the live fire, so the whole chain was verified end-to-end
before spending the bot visit.

## The exposed-endpoint -> file -> flag chain

```
STAGE 1: POST /session -> sessionId (web-chromedriver)
STAGE 2: file:///proc/self/environ -> source -> FLAG env var (web-chromedriver)
         or file:///flag -> the direct read
STAGE 3: the flag path found -> file://<path> -> source (web-chromedriver)
STAGE 4: the flag -> pre-flag
```

The two-read version: `environ` for the flag-in-env case (it names the
path), the direct `/flag` for the flag-file case.

## The session -> loopback -> admin -> flag chain

```
STAGE 1: POST /session -> sessionId
STAGE 2: localhost/admin -> source -> an admin panel / internal API
STAGE 3: execute fetch(localhost/api/flag) -> the flag
STAGE 4: -> pre-flag
```

The browser's loopback position reaches the internal route — the chain
is foothold -> internal reach -> flag.

## The bot -> credential -> replay -> flag chain

```
STAGE 1: stored payload -> the bot's browser (web-chromedriver + xss)
STAGE 2: payload exfils the bot's session cookie/token -> listener
STAGE 3: replay the credential -> authenticated request to the flag page
STAGE 4: the flag in the response -> pre-flag
```

The exfil is not the flag — it is the *credential* that reaches the
flag. The chain extends past the browser harness into a replayed
authenticated request.

## The egress-blocked -> write-back -> read chain

```
STAGE 1: stored payload -> the bot's browser
STAGE 2: payload writes the flag to a same-origin store (profile/note)
STAGE 3: you fetch the store -> the flag
STAGE 4: -> pre-flag
```

Off-origin egress blocked — the flag never leaves; the app's origin
is the channel. The "exfil" is a same-origin write.

## The chain-design principle

Each stage belongs to a class — the browser harness is the connector,
not the whole chain:

- the injection class (`web-xss`) owns the payload
- `web-chromedriver` owns the browser-control stages (reproduce,
  fire, exfil, read)
- the follow-on class (`web-ssti`, `file-read-primitives`,
  `web-command-injection`) owns the escalation

Design the chain so each stage is confirmed locally before the live
fire — a chain is only as confirmed as its weakest unverified stage.
The harness's job is to make the browser-dependent stages verifiable.
