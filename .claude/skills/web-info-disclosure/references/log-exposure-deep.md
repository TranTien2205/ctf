# Exposed logs — deep

Access and error logs served over HTTP leak request paths, tokens, internal IPs, and sometimes credentials in query strings.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no log paths serve content: the channel is closed.

## Highest-cost traps

- Logs can be huge — grep, don't load.
- A log's most interesting entries are usually the ADMIN's requests.
- Log disclosure + log poisoning (user-agent) is a separate bug class.

## Commands

```bash
for p in /access.log /error.log /logs/ /debug.log; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`directory-listing.md` · `backup-archives.md`
