# Editor swap and temp files — case catalogue

Vim .swp, Emacs #file#, nano .save, Windows ~$: the editor's crash-recovery copy of a source file, served as text.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.index.php.swp or .file.swp 200 | vim swap | recover source via vim -r or strings |
| 2 | /file.save or file.bak | editor backup | read source |
| 3 | /~file or #file# | emacs/nano backup | read source |
| 4 | partial reads / range answers | server serves byte ranges | range-recover larger files |

## Falsifier

Falsifier — no swap/temp file for any known filename: no editor leftovers.
