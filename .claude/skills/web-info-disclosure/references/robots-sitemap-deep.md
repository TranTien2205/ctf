# robots.txt and sitemap.xml — deep

The two files meant for crawlers list the paths the author didn't want indexed — a free route map including admin, backup, and dev areas.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — robots.txt is empty/default and sitemap.xml is absent or only lists public pages: no hidden-path disclosure here.

## Highest-cost traps

- A path in robots.txt that 404s may be stale — or may only answer POST/other verbs.
- Sitemap can list thousands of URLs — filter for admin/backup/api/auth patterns, don't walk all.
- robots.txt entries are hints, not guarantees — verify each.

## Commands

```bash
curl -s '$BASE/robots.txt'; curl -s '$BASE/sitemap.xml'
```

## Cross-references

`exposed-artifacts.md` · `debug-endpoints.md`
