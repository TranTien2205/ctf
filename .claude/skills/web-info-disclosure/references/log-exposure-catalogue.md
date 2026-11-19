# Exposed logs — case catalogue

Access and error logs served over HTTP leak request paths, tokens, internal IPs, and sometimes credentials in query strings.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /access.log or /error.log 200 | log served | grep for paths/secrets |
| 2 | /logs/ index | log dir listed | walk it |
| 3 | log inside a backup archive | bundled log | extract |
| 4 | debug.log / app.log / laravel.log | app log | read for internals |

## Falsifier

Falsifier — no log paths serve content: the channel is closed.

## Coverage notes

- Logs can be huge — grep, don't load.
- A log's most interesting entries are usually the ADMIN's requests.
- Log disclosure + log poisoning (user-agent) is a separate bug class.

## Cross-references

`directory-listing.md` · `backup-archives.md`
