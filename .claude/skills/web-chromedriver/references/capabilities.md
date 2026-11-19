# Capabilities — the session capability reference

## The structure

```json
{
  "capabilities": {
    "alwaysMatch": { "...": "..." },
    "firstMatch": [ { "...": "..." } ]
  }
}
```

`alwaysMatch` applies to every session; `firstMatch` is a list of
alternative capability sets the driver may satisfy. Most CTF use needs
only `alwaysMatch`.

## The common capabilities

| Capability | Values | Use |
|---|---|---|
| `browserName` | `chrome`, `firefox`, `MicrosoftEdge` | pick the browser |
| `browserVersion` | a version string | pin a version (Grid) |
| `platformName` | `linux`, `windows`, `mac` | pick the OS (Grid) |
| `goog:chromeOptions` | `{args:[], binary:""}` | Chrome args + binary |
| `moz:firefoxOptions` | `{args:[], binary:""}` | Firefox args + binary |
| `acceptInsecureCerts` | `true`/`false` | accept self-signed |
| `pageLoadStrategy` | `normal`/`eager`/`none` | when `goto` returns |
| `timeouts` | `{script,pageLoad,implicit}` | command timeouts |

## Chrome-specific options

```json
{"goog:chromeOptions": {
  "args": ["--headless=new","--no-sandbox","--disable-dev-shm-usage"],
  "binary": "/usr/bin/chromium",
  "extensions": ["<base64-crx>"],
  "prefs": {"download.default_directory":"/tmp"},
  "debuggerAddress": "localhost:9222"
}}
```

| Key | Use |
|---|---|
| `args` | the Chrome flags — the reproduction-critical list |
| `binary` | a non-default browser binary path |
| `prefs` | profile preferences (download dir, etc.) |
| `debuggerAddress` | attach to an already-running Chrome |
| `extensions` | load an extension (base64 `.crx`) |

## pageLoadStrategy

| Value | `goto` returns when |
|---|---|
| `normal` | the `load` event (default) |
| `eager` | `DOMContentLoaded` |
| `none` | immediately, before anything loads |

`eager`/`none` matter when a page never finishes loading — a payload
that holds a connection open, or a long-polling app — and `goto` would
otherwise hang.

## Timeouts

```json
{"timeouts": {"script": 30000, "pageLoad": 30000, "implicit": 5000}}
```

| Timeout | Governs |
|---|---|
| `script` | how long `execute/async` may run |
| `pageLoad` | how long `navigate` may take |
| `implicit` | how long element-find retries before failing |

## Capability negotiation failures

When `POST /session` fails, the error names the missing capability:

- `session not created: No matching capabilities` -> a `firstMatch` set
  the driver cannot satisfy
- `browserName` not supported -> the driver only does its own browser
- `platformName` mismatch -> a Grid that only serves one platform

Read the error — it tells you which capability the endpoint wants.

## Selenium Grid / remote

A Grid endpoint (`:4444`) routes sessions to nodes by capability —
`platformName`, `browserVersion`, custom `se:` options. For an exposed
Grid, the capabilities you send select which node/browser you get;
weak Grids may give more than you ask for. The commands after session
creation are identical.

## The reproduction capability

When reproducing the challenge's bot, the capability that matters is
`goog:chromeOptions.args` — it carries the flags the bot sets. Read
the bot's launch args and put them in the same place, so the local
browser is the same environment.
