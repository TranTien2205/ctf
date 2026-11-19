# 403 bypasses — verbs, headers, path tricks — case catalogue

A 403 on a real artifact is 'forbidden', not 'absent': alternate verbs, Host tricks, and path forms reopen it.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | GET 403 → HEAD/OPTIONS 200 | verb bypass | read body via the verb that answers |
| 2 | 403 → 200 with X-Forwarded-For: 127.0.0.1 | IP allowlist bypass | spoof the trusted header |
| 3 | 403 → 200 via /./path or //path | normalization gap | path tricks |
| 4 | 403 on /admin → 200 on /admin/ | trailing-slash rule | siblings |

## Falsifier

Falsifier — every verb/header/path variant returns the same 403: the artifact is genuinely forbidden to this surface.
