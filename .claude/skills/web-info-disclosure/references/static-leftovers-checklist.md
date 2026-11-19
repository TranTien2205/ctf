# Static leftovers — OS and editor artifacts — operational checklist

.DS_Store, Thumbs.db, .swp files, node_modules paths, editor temp files: small artifacts that map the directory's real contents.

## Checklist

- [ ] Probe: /.DS_Store /.index.php.swp /Thumbs.db /node_modules/.
- [ ] .DS_Store contains the directory's real file list — parse for names to probe.
- [ ] swp files are vim swap: `vim -r` or strings recovers the edited source.
- [ ] node_modules exposure gives exact dependency versions → gadget_lookup.

## Abort conditions

- .DS_Store is binary — needs a parser, not a text read.
- swp may hold a DIFFERENT version than the live file — note the discrepancy.

## Falsifier

Falsifier — no leftover artifacts serve: the channel is closed.

## Cross-references

`backup-archives.md` · `source-disclosure.md`
