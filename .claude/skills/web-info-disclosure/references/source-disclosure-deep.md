# Source disclosure — served code files — deep

When the server serves source instead of executing it — backup extensions, misconfigured handlers, static mounts of app dirs — you read the application itself.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — source paths return 404/403 or executed output only: no raw source is served. The handout is closed; work black-box.

## Highest-cost traps

- A manifest alone gives versions → gadget_lookup turns them into known-gadget recall.
- Static mounts of /src/ may exclude config files that are still reachable by direct name.
- Served .git is the extreme case — see git-exposure.

## Commands

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
for p in /index.php~ /package.json /composer.json /requirements.txt; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`git-exposure.md` · `backup-archives.md`
