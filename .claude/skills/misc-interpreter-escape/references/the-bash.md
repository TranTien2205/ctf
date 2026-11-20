# Bash jails — $IFS, globs, expansions

Shell keyword blocks yield to `$IFS` (the separator), `???`/`***`
globs, `${var:offset:1}` slicing, backtick/`$()` substitution — a
word never typed is never blocked.

## Word-free

$IFS, globs, ${var:o:1}, escapes — a word never typed is never blocked.

## Word-free

IFS/glob/slice — never typed, never blocked.
