# Decision map — every fork, and which branch to take

## Fork 1: which use?

```
is there an exposed WebDriver endpoint? --yes--> attack surface
is there a bot flow + client-side payload? --yes--> debugging aid
both? -> do the surface first (cheaper read), then the aid
neither? -> class dead
```

## Fork 2: which read primitive? (attack surface)

```
file read works?  --yes--> flag in a file? -> file:// read
execute works?    --yes--> flag in cookie/storage/origin? -> execute read
loopback works?   --yes--> flag on an internal route? -> localhost read
jar works?        --yes--> flag is a cookie? -> GET /cookies
render needed?    --yes--> flag is visual? -> screenshot
```

Pick by *where the flag lives* — the map orders file > route > cookie >
storage > origin > render.

## Fork 3: how to reproduce? (debugging aid)

```
bot source supplied? -> copy spec verbatim
flow observed only?  -> reproduce observed, flag assumptions
neither?             -> weak reproduction, development only
```

## Fork 4: which observability?

```
need console/errors? -> page.on("console"/"pageerror")
need network?        -> page.on("request"/"requestfailed")
need DOM?            -> page.content() / GET /source
need bodies/deep?    -> CDP Network/Runtime
```

## Fork 5: which exfil channel?

```
off-origin fetch ok?      -> fetch to listener
CSP blocks connect-src?   -> img/script subresource
all external blocked?     -> same-origin write-back
short wait?               -> sendBeacon/Image (fire-and-forget)
navigation ok?            -> top.location
```

## Fork 6: local works, live fails?

```
reproduction wrong? -> re-derive URL/cookie/wait/flags/version
channel dead?       -> check tunnel from inside, pivot channel
context wrong?      -> the payload class -> ../web-xss/
"bot" not a browser?-> ../web-ssrf/
layer spent?        -> tools/decide.py -> escalate
```

## Fork 7: flag in hand?

```
flag-shaped string in a live response -> pre-flag gate
a local TESTFLAG/canary               -> development only, not the flag
a sessionId                           -> capability, not a read
```

## The map in one line

Surface first (cheap read), then the aid; pick the read by the flag's
location; pick the exfil by the block; a stall routes to a boundary,
not a sixth variant.
