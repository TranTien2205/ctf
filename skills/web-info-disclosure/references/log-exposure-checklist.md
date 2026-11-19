# Exposed logs — operational checklist

Access and error logs served over HTTP leak request paths, tokens, internal IPs, and sometimes credentials in query strings.

## Checklist

- [ ] Probe: /access.log /error.log /logs/ /log/ /debug.log /app.log /storage/logs/laravel.log.
- [ ] grep for: flag{, password, token, /admin, internal IPs, user-agents.
- [ ] Log URLs reveal endpoints that don't appear anywhere else.
- [ ] Query-string tokens in logs are sometimes still valid sessions.

## Abort conditions

- Logs can be huge — grep, don't load.
- A log's most interesting entries are usually the ADMIN's requests.
- Log disclosure + log poisoning (user-agent) is a separate bug class.

## Falsifier

Falsifier — no log paths serve content: the channel is closed.

## Cross-references

`directory-listing.md` · `backup-archives.md`
