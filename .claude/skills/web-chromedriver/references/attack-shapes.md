# Attack shapes — the named exploit patterns

## Shape 1: the debugging-aid loop (most common)

```
reproduce bot locally -> develop payload -> confirm fires -> fire live once
```

The dominant use. Buys: console, DOM, network, unlimited iterations.
Anchor: `apexsurvive`.

## Shape 2: the exposed-endpoint file read

```
POST /session -> navigate file:///flag -> GET /source -> flag
```

The direct capability. Buys: a file read as the driver's user, plus
loopback HTTP reach. The flag is in the `source` response.

## Shape 3: the JS-in-browser read (nav blocked)

```
POST /session -> execute/sync fetch("file:///flag") -> the file text
```

When `file://` navigation is blocked but `execute` runs. The JS file
read is a separate primitive from the navigation one — test both.

## Shape 4: the loopback pivot

```
POST /session -> navigate http://localhost/admin -> GET /source
```

The browser's origin reaches routes the app only serves locally —
admin panels, debug endpoints, internal APIs. Buys: the loopback
attack surface through the browser's position.

## Shape 5: the authenticated-context read

```
execute document.cookie / localStorage / fetch(same-origin-api)
```

The session inherits the browser's origin and any cookies it holds —
read the flag from `document.cookie`, `localStorage`, or a same-origin
API the browser can reach.

## Shape 6: the same-origin write-back (egress blocked)

```
payload writes flag into a same-origin store -> you read the store
```

When the bot cannot exfil off-origin. The flag is written to a profile
field, a stored comment, an API — anywhere on the app's origin you can
then read. The channel is the app itself.

## Shape 7: the screenshot read

```
navigate to the flag page -> GET /screenshot -> read the PNG
```

When the flag renders visually but the text source is mangled or the
read is a rendered page. The PNG is the artifact carrying the flag.

## Shape 8: the multi-stage chain (the real CTF shape)

```
stored XSS fires in bot -> bot's cookie/token exfil'd -> you replay it -> flag page
```

`apexsurvive`'s actual shape: the payload does not read the flag
directly — it exfiltrates the bot's credential or triggers a state
change, and you use that to reach the flag. The local bot reproduces
each stage before the live fire.

## Choosing the shape

| Observation | Shape |
|---|---|
| admin bot + client-side payload | 1 (then 8 for the real chain) |
| `POST /session` answers | 2, 3, 4, 5 by which read works |
| bot can't exfil off-origin | 6 |
| flag renders but text is mangled | 7 |
| flag needs the bot's credential | 8 |

Most real challenges are shape 1 developing into shape 8 — the local
loop builds the multi-stage chain one confirmed stage at a time.
