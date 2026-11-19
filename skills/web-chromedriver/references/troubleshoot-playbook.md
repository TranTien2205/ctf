# Troubleshoot playbook — the structured fix-it guide

## Play 1: driver won't start

```
SYMPTOM                          DIAGNOSIS                    FIX
session not created: version     driver/browser mismatch      match major version
chrome not reachable             no browser binary            set binary/binary_location
DevToolsActivePort               container flags missing      --no-sandbox --disable-dev-shm-usage
hangs on create                  leaked session holds port    GET /sessions -> DELETE, or pkill
unknown error / crash            /dev/shm too small           --disable-dev-shm-usage
permission denied                sandbox in container         --no-sandbox
```

## Play 2: reproduction diverges from live

```
DIVERGENCE                       CHECK                         FIX
different DOM/context            bot's URL/auth/frame           re-derive; navigate to the real URL
flag cookie missing              add_cookie domain/path/flags   match the bot's exactly
payload too slow for wait        measure payload time           shorten async; beacon/Image
version behaviour differs        the pinned version             install matching browser
headless fingerprint differs     navigator.webdriver et al      match the bot's automation flags
page renders differently         the route/context              same DOM as the bot's view
```

## Play 3: the read fails

```
SYMPTOM                          DIAGNOSIS                    FIX
file:// nav error page           scheme blocked                execute fetch("file://")
file not found                   wrong path                    try /etc/passwd to distinguish
empty source                     empty/binary file             text canary; base64 for binary
localhost same-as-external       no internal surface           the browser's reach is external-only
execute permission error         script gated                  nav reads only; or CDP on 9222
screenshot blank                 old headless mode             --headless=new
source = error page              wrong page/redirect           GET /url confirms where it is
```

## Play 4: the exfil never lands

```
SIGNAL                           DIAGNOSIS                    FIX
REQ logged, listener silent      tunnel unreachable            goto own tunnel inside driver
requestfailed / RESP:0           egress filter / CSP           same-origin write-back; subresource
no REQ at all                    exfil branch never ran        the payload's logic — read console
ERR_SSL                          cert rejected                 --ignore-certificate-errors / http://
beacon works, fetch doesn't      connect-src blocks fetch      the img/script channel
interstitial page                tunnel confirm page           a tunnel without it
```

## Play 5: the flag won't confirm

```
SYMPTOM                          DIAGNOSIS                    FIX
flag-shaped string, gate fails   it's a candidate              the live response must carry it
TESTFLAG on listener             it's a canary                 not the flag — development only
local marker fires               development evidence          not target proof
sessionId returned               capability, not a read        the file:// source is the read
```

## Play 6: the diagnosis-first order

```
1. which stage died?  -> console + pageerror (the thrown error)
2. which request?     -> request + requestfailed (what left/blocked)
3. which context?     -> the rendered DOM (where the value landed)
4. which timing?      -> the wait (did it fit the budget)
5. which property?    -> the reproduction (URL/cookie/wait/flags/version)
```

The four channels + the reproduction properties name the failing
stage; the fix is for that stage, not a blanket retry.

## Play 7: the escalation

```
reproduction won't match   -> re-derive each property; the bot version
payload won't fire locally -> the context -> ../web-xss/
channel dead               -> the channel pivots -> evasion.md
read blocked               -> execute/localhost/CDP alternates
not a browser              -> ../web-ssrf/
mechanism layer spent      -> tools/decide.py -> escalate rung
```
