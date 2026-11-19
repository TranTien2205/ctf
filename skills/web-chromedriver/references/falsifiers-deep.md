# Falsifiers deep — the kill-map mechanics

## The falsifier structure

A falsifier is a *measured state that ends a mechanism layer* — three
parts:

```
probe:        the command that produces the state
kill state:   the observation that closes the layer
re-open:      the observation that would re-open it
```

A cell without a re-open condition is an assertion, not a measurement
— record what *would* change the answer.

## Cell: endpoint exposure

```
probe: POST /session on 9515,4444,/wd/hub/session,/session,9222
kill:  all refused / 404 / connection error
re-open: any port/route returns a sessionId or JSON error
```

The kill is *all* ports refused — a single refused port is one dead
route, not a dead class. The re-open keeps the search honest: a new
port discovery re-opens the cell.

## Cell: file-read primitive

```
probe: nav file:///etc/passwd -> source
kill:  error page | blocked scheme | empty source
re-open: execute fetch("file://") works; a different scheme;
         the error was path-specific not scheme-blocked
```

The subtlety: a `file://` *navigation* block does not always kill the
*JS* `fetch("file://")` — the two are separate primitives. Test both
before recording the cell dead.

## Cell: JS execution

```
probe: execute/sync return 1+1
kill:  permissions/disabled/unsupported error
re-open: execute/async allowed; CDP Runtime.evaluate on 9222;
         a different capability enables it
```

`execute` dead means navigation-only reads still live — the cell
closes the JS primitive, not the whole surface.

## Cell: loopback reach

```
probe: nav localhost/{admin,debug,metrics,internal} -> source
kill:  same-as-external | refused | nothing extra reachable
re-open: a different internal port/route answers
```

## Cell: faithful reproduction

```
probe: build local bot from source/observation
kill:  no source AND no observable properties to copy
re-open: bot source found; more behaviour observed
```

The honest cell — a failed reproduction is not "the class is dead",
it is "development is less efficient". Record it as a weakened state.

## Cell: exfil channel

```
probe: fetch/goto own tunnel from inside the driver
kill:  interstitial | refused | filtered | RESP:0
re-open: a different tunnel; same-origin channel; DNS; beacon
```

## Cell: flag-in-reach

```
probe: sweep surfaces — file, cookie, storage, DOM, localhost, render
kill:  flag on no surface the browser reaches
re-open: a new surface (route/store/path) is found
```

## The compound rule

The class is dead when the *use* is dead — attack surface AND
debugging aid. One live use keeps it alive. Cells within a use are
independent — a dead file-read does not kill the loopback reach.

## The measured-negative rule

Every cell records the probe + the kill state + the re-open — the
next run reads the kill map and skips dead cells without re-probing,
and knows exactly what would re-open each.
