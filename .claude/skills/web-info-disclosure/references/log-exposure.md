# Exposed logs

Access and error logs served over HTTP leak request paths, tokens, internal IPs, and sometimes credentials in query strings.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /access.log or /error.log 200 | log served | grep for paths/secrets |
| /logs/ index | log dir listed | walk it |
| log inside a backup archive | bundled log | extract |
| debug.log / app.log / laravel.log | app log | read for internals |

## Steps

1. Probe: /access.log /error.log /logs/ /log/ /debug.log /app.log /storage/logs/laravel.log.
2. grep for: flag{, password, token, /admin, internal IPs, user-agents.
3. Log URLs reveal endpoints that don't appear anywhere else.
4. Query-string tokens in logs are sometimes still valid sessions.

## Falsifier

Falsifier — no log paths serve content: the channel is closed.

## Traps

- Logs can be huge — grep, don't load.
- A log's most interesting entries are usually the ADMIN's requests.
- Log disclosure + log poisoning (user-agent) is a separate bug class.

## Commands

```bash
for p in /access.log /error.log /logs/ /debug.log; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`directory-listing.md` · `backup-archives.md`
