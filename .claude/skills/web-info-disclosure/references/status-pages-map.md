# Status, metrics, and info pages — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /server-status Apache page | Apache status | vhosts, current requests |
| /phpinfo.php or phpinfo output | full PHP config | env, paths, modules |
| /metrics with prometheus format | metrics exposed | internal names |
| /health or /status with internals | health detail | dependency map |

## Falsifier

Falsifier — no status/info page exists or all are stripped to 'OK': the ops surface is closed.
