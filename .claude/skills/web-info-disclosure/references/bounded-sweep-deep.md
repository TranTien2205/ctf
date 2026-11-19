# The bounded sweep — scope discipline — deep

Info-disclosure sweeps are bounded by definition: a short list of well-known paths, not a scanner. The class lives inside the supplied surface.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — canonical list all-negatives AND no evidence names a custom path: the disclosure surface is closed.

## Highest-cost traps

- Directory brute-forcing (ffuf/gobuster wide) is not this class — it's a scope violation on shared infra.
- A path you invent has no evidence to stand on — don't probe it.
- The sweep is once per target; re-run only when new evidence names a path.

## Commands

```bash
for p in /.git/HEAD /.env /robots.txt /sitemap.xml /backup.zip /actuator /server-status /.DS_Store /phpinfo.php /swagger.json; do code=$(curl -s -o /tmp/r -w '%{http_code}' --max-time 8 "$BASE$p"); echo "$p $code $(wc -c </tmp/r)"; done
```

## Cross-references

`exposed-artifacts.md` · `catchall-falsifier.md`
