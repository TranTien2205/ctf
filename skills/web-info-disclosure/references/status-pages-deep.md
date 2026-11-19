# Status, metrics, and info pages — deep

server-status, phpinfo, /metrics, health endpoints: operational surfaces that leak internals — vhosts, loaded modules, request URLs, uptime internals.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no status/info page exists or all are stripped to 'OK': the ops surface is closed.

## Highest-cost traps

- server-status request list leaks OTHER users' URLs — including tokens in query strings.
- phpinfo() prints _ENV — the same secrets as .env.
- A metrics page is a map for other attacks — capture the names.

## Commands

```bash
for p in /server-status /phpinfo.php /metrics /health; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`debug-endpoints.md` · `env-config-leaks.md`
