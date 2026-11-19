# .DS_Store parsing

macOS directory metadata: a binary file listing the directory's real contents — filenames, including ones never linked.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.DS_Store 200 binary ~few KB | dir contents | parse for filenames |
| names inside reveal .env/backup/flag names | targeted probes | probe each |

## Steps

1. Fetch /.DS_Store (and per-dir: /uploads/.DS_Store etc.).
2. Parse with a .DS_Store parser or strings + structure knowledge — the file list is the prize.
3. Each filename found is a targeted probe.
4. Recurse: a .DS_Store in a found dir lists that dir's contents.

## Falsifier

Falsifier — no .DS_Store on any dir: the channel is closed (Windows boxes use Thumbs.db instead).

## Traps

- It's binary — strings gives partial names; a real parser gives the full list.
- Hidden files appear in .DS_Store even though directory listing is off.
- Per-directory: probe .DS_Store inside every discovered directory.

## Commands

```bash
curl -s '$BASE/.DS_Store' -o ds && strings ds | grep -iE 'flag|env|bak|sql|key'
```

## Cross-references

`static-leftovers.md` · `directory-listing.md`
