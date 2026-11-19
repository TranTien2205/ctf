# tools/web/http_probe.py — the sanctioned request+response — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url required, --challenge required | hooks integration | evidence-ready |
| --emit runs pre-probe+post-probe | verified loop | post-probe quoted |
| --header/--body/--method | request shaping | as needed |
| --body-chars bounds the excerpt | response size | for big bodies |

## Falsifier

Falsifier — the response is the catch-all body: no disclosure, record the negative.
