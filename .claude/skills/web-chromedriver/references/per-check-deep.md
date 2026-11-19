# Per-check deep — each gate, with its probe and pass/fail

## Gate: exposure

- **Probe**: `POST /session` (or `GET /json`) on each candidate port/route.
- **Pass**: `sessionId` / a JSON error naming a capability issue.
- **Fail**: connection refused / 404 — the surface is dead at that endpoint.
- **Record**: which endpoint answered, the `browserName`, the version.
- **Note**: a JSON error is "answering but failing" — different from
  refused; try the legacy `desiredCapabilities` form.

## Gate: file-read

- **Probe**: `nav file:///etc/passwd` -> `GET /source`.
- **Pass**: the source contains `root:x:0:0` (a known line).
- **Fail**: Chrome error page / blocked scheme / empty.
- **Then**: if nav fails, `execute` `fetch("file:///etc/passwd")` — the
  JS form is a separate primitive.
- **Record**: which form (nav or JS) reads, and the excerpt.

## Gate: JS-execution

- **Probe**: `execute/sync` `return 1+1`.
- **Pass**: returns `2`.
- **Fail**: permissions/unsupported/disabled error.
- **Then**: `execute/async`, or CDP `Runtime.evaluate` on 9222.
- **Record**: which JS form runs; a dead JS gate leaves navigation reads.

## Gate: loopback

- **Probe**: `nav localhost/{admin,debug,metrics,api}` -> `source`.
- **Pass**: content the external view lacks (an admin panel, a route).
- **Fail**: same-as-external, refused, or nothing extra.
- **Record**: the internal-only route that answered.

## Gate: cookie-jar

- **Probe**: `GET /session/{id}/cookies` on the flag's origin.
- **Pass**: the flag/named cookie present.
- **Fail**: empty jar or the flag cookie absent — the flag is not
  cookie-carried; look to another surface.
- **Record**: the cookie name + whether `document.cookie` sees it.

## Gate: reproduction-fidelity

- **Probe**: local bot with derived properties -> `page.content()` vs live.
- **Pass**: the DOM/context matches on the behaviour axes.
- **Fail**: a divergence (missing cookie, wrong DOM, wrong context).
- **Record**: which property diverged; the reproduction is the bug.
- **Note**: an unmatched reproduction invalidates local confirmations.

## Gate: exfil-channel

- **Probe**: inside the driver, `fetch`/`goto` your own tunnel URL.
- **Pass**: `page.content()`/response is your real body.
- **Fail**: an interstitial page, a refusal, a CSP block.
- **Record**: the channel that works; a dead channel is a `tornadoservice`.

## Gate: flag-candidate

- **Probe**: `tools/hooks.py pre-flag --value <s> --source <resp> --evidence <ex>`.
- **Pass**: the gate confirms against a live response/artifact.
- **Fail**: still a candidate — not a flag until the gate passes.

## The gate order

```
exposure -> file-read/js/loopback/jar (the primitive map)
        -> reproduction-fidelity (aid) -> exfil-channel -> flag
```

Each gate is one cheap probe; a fail routes to the gate's fallback.
