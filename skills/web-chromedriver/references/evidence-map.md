# Evidence map — what proves each claim, precisely

## The claims and their proofs

| Claim | The proof | The response that carries it |
|---|---|---|
| a driver endpoint is exposed | a `sessionId` in a `POST /session` response | the `POST /session` JSON body |
| a Grid is exposed | node inventory | `GET :4444/status` body |
| CDP is exposed | a target list | `GET :9222/json` body |
| a file read works | the file's text in `source` | `GET /source` body |
| JS execution works | `return 1+1` -> `2` | the `execute` JSON body |
| loopback is reachable | internal content in `source` | `GET /source` of a `localhost` nav |
| the jar is readable | the cookie list | `GET /cookies` body |
| a flag cookie is present | the named cookie in the jar | `GET /cookies` body |
| the flag is on a page | flag text in `source`/`execute` | the `source`/`execute` body |
| the flag is rendered | the flag in the PNG | the decoded `screenshot` |
| the payload executes | a console marker / a network hit | the local-bot trace (development) |
| the exfil left | a listener hit with the value | your listener's request log |
| the flag was exfil'd | a listener hit with the flag | your listener's request log |

## The response-to-evidence rule

For `tools/hooks.py post-probe --verdict confirms`, the `--evidence`
must be a substring of `--response` — the quote is *checked*:

- **file-read confirm**: `--response` = the `GET /source` body,
  `--evidence` = `root:x:0:0:` or the flag line inside it
- **flag-cookie confirm**: `--response` = the `GET /cookies` body,
  `--evidence` = the flag cookie's value
- **endpoint confirm**: `--response` = the `POST /session` JSON,
  `--evidence` = the `sessionId` field
- **exfil confirm**: `--response` = the listener's logged request,
  `--evidence` = the flag-shaped value in the query/body

## The three tiers, applied

**Development evidence** — the local bot's console, network, DOM.
Proves the payload works in *your* reproduction. Never a flag proof,
never a target finding — the reproduction is yours, not the target's.

**Capability evidence** — a `sessionId`, a `1+1` return, a `file://`
source. Proves the endpoint exposes the primitive. A capability, not
an exploit — it says the reach exists, not that the flag was taken.

**Impact evidence** — the live exfil on your listener, the flag-
bearing `source`/`cookies`/`screenshot` from the exposed endpoint.
The only tier that carries the flag.

## The provenance rule

Save the *proving bytes*, not just the conclusion:

- the `GET /source` body, not "the file was there"
- the listener's request log line, not "the flag came back"
- the decoded PNG, not "the flag was in the image"
- the `GET /cookies` body, not "the cookie was set"

The bytes are the evidence; the conclusion is what they show.

## The candidate boundary

A flag-shaped string in a live response is a *candidate* — it is the
flag only after `tools/hooks.py pre-flag` gates it:

- **live exfil listener log** -> the response carrying the flag
- **the `source`/`cookies`/`screenshot` body** -> the artifact carrying it

A `TESTFLAG`, a `CANARY`, a marker — development signals, never a flag.

## The negative evidence

A measured dead end is evidence of the *closed* layer — record the
probe and the state, not just "didn't work":

- `POST /session` refused -> "endpoint not exposed at :PORT"
- `file://` nav error page -> "file read blocked at scheme"
- `execute` permissions error -> "JS primitive gated"
- `REQ` to tunnel, listener silent -> "channel unreachable for headless"

Each is a kill-map entry — evidence of the dead cell with its re-open.
