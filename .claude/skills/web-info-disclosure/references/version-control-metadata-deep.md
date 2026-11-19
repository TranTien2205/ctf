# VCS metadata beyond .git — deep

.svn, .hg, .bzr and partial .git states each leak differently — different file layouts, different recovery paths.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — none of the VCS metadata paths return real metadata: no repository is exposed.

## Highest-cost traps

- Modern SVN (1.7+) uses wc.db sqlite — fetch it and query locally.
- Partial recovery is still a finding: the filenames alone reveal structure.
- A .git with only pack files needs the pack protocol — git_dumper reports this honestly.

## Commands

```bash
for p in /.svn/entries /.svn/wc.db /.hg/requires /.git/HEAD; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`git-exposure.md` · `tools-git-dumper.md`
