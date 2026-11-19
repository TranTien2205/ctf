# .DS_Store parsing — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.DS_Store 200 binary ~few KB | dir contents | parse for filenames |
| names inside reveal .env/backup/flag names | targeted probes | probe each |

## Falsifier

Falsifier — no .DS_Store on any dir: the channel is closed (Windows boxes use Thumbs.db instead).
