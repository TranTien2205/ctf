# Exposed logs — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /access.log or /error.log 200 | log served | grep for paths/secrets |
| /logs/ index | log dir listed | walk it |
| log inside a backup archive | bundled log | extract |
| debug.log / app.log / laravel.log | app log | read for internals |

## Falsifier

Falsifier — no log paths serve content: the channel is closed.
