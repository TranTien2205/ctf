# .DS_Store parsing — case catalogue

macOS directory metadata: a binary file listing the directory's real contents — filenames, including ones never linked.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.DS_Store 200 binary ~few KB | dir contents | parse for filenames |
| 2 | names inside reveal .env/backup/flag names | targeted probes | probe each |

## Falsifier

Falsifier — no .DS_Store on any dir: the channel is closed (Windows boxes use Thumbs.db instead).
