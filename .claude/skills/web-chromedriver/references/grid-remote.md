# Grid and remote drivers — the shared/exposed variant

## What a Grid is

Selenium Grid routes `POST /session` to nodes by capability — a hub
on `:4444` that fans out to browser nodes. The WebDriver commands are
identical; the difference is the capability negotiation picks which
node/browser you land on.

## Detecting a Grid vs a plain driver

| Signal | Meaning |
|---|---|
| `:4444` responds, `:9515` does not | a Grid hub, not a bare driver |
| `/wd/hub/status` returns node info | a Grid (older API path) |
| `/status` shows `nodes`/`slots` | a Grid4 hub |
| `se:` capabilities in errors | Grid4-specific capability space |

```bash
curl -s http://TARGET:4444/status | python3 -m json.tool
curl -s http://TARGET:4444/wd/hub/status | python3 -m json.tool   # older
```

A Grid's status often lists its nodes and their browsers — free recon
of which browser/version/OS you can request.

## Capability routing

```json
{"capabilities":{"alwaysMatch":{
  "browserName":"chrome",
  "platformName":"linux",
  "browserVersion":"120"
}}}
```

On a Grid these select a node — a misconfigured or permissive Grid may
accept more than it should, or default to a node with different
privileges than expected. The browser you get is whichever node the
capabilities match.

## The file read on a Grid node

The `file://` read works the same — but it reads files on the *node's*
filesystem, which may be a different container/user than the app. The
flag path is the node's, and the node's network position (what
`localhost` means to it) is its own — internal services it reaches may
differ from the app's.

## Auth and weak Grids

Some Grids are wide open (no auth on `POST /session`), some gate
behind a token. An open Grid is the same capability as an open driver
— file read, loopback reach, JS execution — plus the recon of seeing
all its nodes. A token-gated Grid routes to `../web-auth-session/` for
the auth bypass first.

## The session capacity concern

A shared Grid has limited slots — leaked sessions exhaust it and the
bot stops working. Same discipline as a single driver, sharper: a
shared Grid is a shared resource, and holding sessions is a shared-
instance write.

## Remote drivers that are not Grid

A bare `chromedriver` exposed on a network port, a managed cloud
driver (BrowserStack-style), or a `docker-selenium` container — all
answer the same `POST /session`. The Grid distinction is the
capability-routing layer; everything else is the same command set.
