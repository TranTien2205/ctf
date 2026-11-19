# Static leftovers — OS and editor artifacts

.DS_Store, Thumbs.db, .swp files, node_modules paths, editor temp files: small artifacts that map the directory's real contents.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.DS_Store 200 binary | macOS dir metadata | parse for filenames |
| /.index.php.swp or .file.swp | vim swap with source | recover source |
| Thumbs.db | Windows dir contents | parse for names |
| /node_modules/ paths resolve | deps exposed | gadget versions |

## Steps

1. Probe: /.DS_Store /.index.php.swp /Thumbs.db /node_modules/.
2. .DS_Store contains the directory's real file list — parse for names to probe.
3. swp files are vim swap: `vim -r` or strings recovers the edited source.
4. node_modules exposure gives exact dependency versions → gadget_lookup.

## Falsifier

Falsifier — no leftover artifacts serve: the channel is closed.

## Traps

- .DS_Store is binary — needs a parser, not a text read.
- swp may hold a DIFFERENT version than the live file — note the discrepancy.

## Commands

```bash
for p in /.DS_Store /.index.php.swp /Thumbs.db; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`backup-archives.md` · `source-disclosure.md`
