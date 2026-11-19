# Field manual — the operational runbook

## Situation 1: admin bot + a client-side payload

```
1. read the bot source -> URL, cookie, wait, flags
2. local driver, same flags -> reproduce
3. four hooks on -> canary -> iterate -> confirm
4. check the exfil channel from inside the driver
5. fire live once -> listener -> pre-flag
```

The discipline: local development first, live fire once. `apexsurvive`.

## Situation 2: an exposed driver endpoint

```
1. POST /session -> sessionId
2. file read? nav file:///etc/passwd + source
3. JS? execute return 1+1
4. loopback? nav localhost/* + source
5. cookie jar? GET /cookies
6. locate flag surface -> read -> pre-flag -> DELETE
```

The reads cover file/route/cookie/DOM/render — pick by flag location.

## Situation 3: a Grid endpoint

```
1. GET :4444/status -> node inventory
2. POST /session with capabilities -> a node session
3. same primitive probes — reads hit the NODE's fs/network
4. note: node's localhost != app's localhost possibly
```

## Situation 4: CDP exposed (port 9222)

```
1. GET /json -> targets + webSocketDebuggerUrl
2. attach ws -> Page.navigate file:///flag
3. Page.captureScreenshot or Runtime.evaluate -> the read
```

## Situation 5: payload fires locally, dead at live bot

```
1. re-derive the reproduction: URL/cookie/wait/flags/version
2. is it a real browser bot? -> JS canary
3. is the wait long enough? -> shorten the payload's async work
4. is the channel dead? -> tunnel interstitial check
```

## Situation 6: egress blocked

```
1. is off-origin blocked but same-origin open? -> write-back channel
2. CSP blocks fetch? -> Image/script/beacon subresource
3. all external dead? -> store the flag on the app's origin, read it back
```

## Situation 7: the read is blocked

```
1. file:// nav blocked -> execute fetch("file://")
2. execute blocked -> navigation-only: file/localhost + source/screenshot
3. localhost sandboxed -> read the app's own origin instead
```

## The discipline that runs through all of it

- canary before exfil
- DOM over response body
- channel check before a bot visit
- faithful reproduction (copy the spec)
- always `DELETE` sessions
- `pre-flag` every candidate
- record dead ends as measured states
