# .DS_Store parsing — deep

macOS directory metadata: a binary file listing the directory's real contents — filenames, including ones never linked.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no .DS_Store on any dir: the channel is closed (Windows boxes use Thumbs.db instead).

## Highest-cost traps

- It's binary — strings gives partial names; a real parser gives the full list.
- Hidden files appear in .DS_Store even though directory listing is off.
- Per-directory: probe .DS_Store inside every discovered directory.

## Commands

```bash
curl -s '$BASE/.DS_Store' -o ds && strings ds | grep -iE 'flag|env|bak|sql|key'
```

## Cross-references

`static-leftovers.md` · `directory-listing.md`
