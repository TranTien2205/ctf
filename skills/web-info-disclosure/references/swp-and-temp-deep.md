# Editor swap and temp files — deep

Vim .swp, Emacs #file#, nano .save, Windows ~$: the editor's crash-recovery copy of a source file, served as text.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no swap/temp file for any known filename: no editor leftovers.

## Highest-cost traps

- The swap file's name pattern is .<name>.swp in the same directory.
- Multiple .swo/.swn files exist for crashed multi-session edits.
- A stale .swp may hold a flag-bearing version since overwritten.

## Commands

```bash
for p in /.index.php.swp /index.php~ /index.php.bak /index.php.old; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`static-leftovers.md` · `source-disclosure.md`
