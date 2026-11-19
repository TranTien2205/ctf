# Static leftovers — OS and editor artifacts — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.DS_Store 200 binary | macOS dir metadata | parse for filenames |
| /.index.php.swp or .file.swp | vim swap with source | recover source |
| Thumbs.db | Windows dir contents | parse for names |
| /node_modules/ paths resolve | deps exposed | gadget versions |

## Falsifier

Falsifier — no leftover artifacts serve: the channel is closed.
