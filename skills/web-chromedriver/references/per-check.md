# Per-check — the gate each primitive must pass

## The exposure check

- **Question**: does a WebDriver endpoint answer?
- **Probe**: `POST /session` on `:9515`, `:4444`, `/wd/hub/session`,
  `/session`.
- **Pass**: a `sessionId` in the JSON response.
- **Fail-safe**: connection refused / 404 -> the surface use dies.
- **Record**: which port/route answered, the browserName it reported.

## The file-read check

- **Question**: does `file://` navigation return a file?
- **Probe**: navigate to `file:///etc/passwd` (always present on Linux).
- **Pass**: `GET /source` contains the file's text.
- **Fail-safe**: error page / blocked scheme -> try `execute` `fetch`.
- **Record**: the source excerpt carrying a known line (`root:x:0:0`).

## The JS-capability check

- **Question**: does `execute` run in the page?
- **Probe**: `execute/sync` `return 1+1`.
- **Pass**: returns `2`.
- **Fail-safe**: permissions error -> the JS primitive is dead; navigation-only.
- **Record**: the returned value.

## The loopback check

- **Question**: can the browser reach the app's loopback routes?
- **Probe**: navigate `http://localhost/` and `/admin`, `/debug`, known
  internal paths.
- **Pass**: `source` returns content the external view lacks.
- **Fail-safe**: same-as-external or refused -> no loopback surface.
- **Record**: the internal-only path that answered.

## The reproduction-fidelity check

- **Question**: does the local bot match the challenge's bot?
- **Probe**: run the local bot with the derived flags/wait/cookie; navigate
  to the live URL; compare the rendered page to the live view.
- **Pass**: the DOM/context matches on the axes that matter.
- **Fail-safe**: a divergence (missing cookie, wrong DOM) -> the
  reproduction is the bug, fix before developing.
- **Record**: which properties are confirmed vs assumed.

## The channel check

- **Question**: can a headless client reach your exfil endpoint?
- **Probe**: from inside the driver, `fetch`/`goto` your own URL.
- **Pass**: `content()` shows your real body, not an interstitial.
- **Fail-safe**: interstitial/refused -> the channel is dead for headless.
- **Record**: the tunnel/endpoint that works.

## The cookie check

- **Question**: is the flag in the browser's cookie jar?
- **Probe**: `GET /cookies` (jar) and `execute` `document.cookie` (JS view).
- **Pass**: the flag/named cookie present in either.
- **Fail-safe**: absent -> the flag is not cookie-carried; look elsewhere.
- **Record**: which view surfaced it (jar reads HttpOnly, JS does not).

## The flag-candidate check

- **Question**: is the recovered string the flag?
- **Probe**: `tools/hooks.py pre-flag --value <candidate> --source <response> --evidence <excerpt>`.
- **Pass**: the gate confirms it against a live response/artifact.
- **Fail-safe**: a candidate is not a flag until the gate passes it.

Each check is one cheap probe with a pass/fail — run them in order,
and a fail at any gate routes to the fallback in `per-mechanism.md`.
