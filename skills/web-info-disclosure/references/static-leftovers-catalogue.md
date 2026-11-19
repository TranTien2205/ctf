# Static leftovers — OS and editor artifacts — case catalogue

.DS_Store, Thumbs.db, .swp files, node_modules paths, editor temp files: small artifacts that map the directory's real contents.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.DS_Store 200 binary | macOS dir metadata | parse for filenames |
| 2 | /.index.php.swp or .file.swp | vim swap with source | recover source |
| 3 | Thumbs.db | Windows dir contents | parse for names |
| 4 | /node_modules/ paths resolve | deps exposed | gadget versions |

## Falsifier

Falsifier — no leftover artifacts serve: the channel is closed.

## Coverage notes

- .DS_Store is binary — needs a parser, not a text read.
- swp may hold a DIFFERENT version than the live file — note the discrepancy.

## Cross-references

`backup-archives.md` · `source-disclosure.md`
