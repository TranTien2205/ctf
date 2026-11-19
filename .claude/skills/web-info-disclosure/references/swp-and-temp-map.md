# Editor swap and temp files — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.index.php.swp or .file.swp 200 | vim swap | recover source via vim -r or strings |
| /file.save or file.bak | editor backup | read source |
| /~file or #file# | emacs/nano backup | read source |
| partial reads / range answers | server serves byte ranges | range-recover larger files |

## Falsifier

Falsifier — no swap/temp file for any known filename: no editor leftovers.
