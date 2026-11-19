# Negative results deep — the kill-map writing discipline

## Why negatives are the asset here

The scarcest resource is the live bot's visit count — every dead end
recorded as a measurement prevents re-walking it on a later run. The
kill map is what turns "we tried a lot" into "we measured which cells
are dead and why".

## The cell record

```
cell:        which mechanism layer
probe:       the command that produced the state
observation: the response / behaviour seen
closes:      what it rules out
re-open:     what would re-open it
```

## The cells, written out

### endpoint-exposure

```
probe: POST /session on 9515,4444,/wd/hub/session,/session,9222/json
obs:   all refused/404
closes: attack-surface use on this host:port set
re-open: another port/route answers; a Grid found; a proxied route
```

### file-read

```
probe: nav file:///etc/passwd -> source; execute fetch("file:///etc/passwd")
obs:   nav -> Chrome error page; fetch -> network error
closes: file-read primitive (both nav and JS forms)
re-open: a different scheme; a capability enabling it; CDP on 9222
```

### js-execution

```
probe: execute/sync return 1+1; execute/async
obs:   sync -> permissions error; async -> same
closes: JS-in-browser primitive (cookie/storage/fetch reads)
re-open: a capability enabling it; CDP Runtime.evaluate
```

### loopback-reach

```
probe: nav localhost/{admin,debug,metrics} + :INTERNAL -> source
obs:   same-as-external or refused on each
closes: loopback-origin surface
re-open: a different internal port; an alias (127.0.0.1, [::1])
```

### reproduction

```
probe: build local bot from bot-source/observation
obs:   no source, no observable URL/cookie/wait/flags
closes: faithful local development
re-open: bot source found; more of the flow observed
note:  weakens the debug use; does not kill the class
```

### exfil-channel

```
probe: fetch/goto own tunnel from inside the driver
obs:   interstitial page returned, not the listener body
closes: that tunnel/channel for headless
re-open: a different tunnel; same-origin write-back; beacon; DNS
```

### flag-in-reach

```
probe: sweep surfaces — file paths, cookie jar, localStorage, DOM,
       localhost routes, screenshot
obs:   flag-shaped string on none
closes: attack-surface use for the searched flag path
re-open: a new surface (route/store/path) found
```

### bot-flow

```
probe: report/admin-visit flow; JS-execution canary to the "bot"
obs:   no bot flow; canary proves no JS/DOM/cookies in the visitor
closes: debugging-aid use — the "bot" is a server fetch -> ../web-ssrf/
re-open: a real bot flow found
```

## The compound record

The class is dead when *both* uses are dead — record the compound:

```
web-chromedriver: DEAD
  attack surface: POST /session refused on all ports (endpoint-exposure)
  debugging aid:  no bot flow; JS canary dead (bot-flow)
```

## The honest "cannot verify"

When the reproduction is on assumptions, record it as unverifiable,
not dead:

```
reproduction: PARTIAL — URL/cookie observed, wait/flags assumed.
  locally-confirmed payload is weaker evidence; live fire is the test.
```

## The re-open sweep

Before declaring the class dead, sweep each cell's re-open once — a
new port, a different scheme, a CDP endpoint, a bot source re-found.
The kill map is only as good as the re-open check that confirmed each
cell stayed dead.
