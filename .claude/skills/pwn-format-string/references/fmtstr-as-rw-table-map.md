# The fmtstr read/write table — the complete primitive set — map

Companion to `fmtstr-as-rw-table.md`.

| Specifier | Effect | Arg use |
|---|---|---|
| %p | print arg as pointer | read |
| %x | print arg as hex | read |
| %s | print *arg as string | arb-read |
| %c | print arg as char | count-pad |
| %d/%i | print arg as int | count-pad |
| %n | write count to *arg | arb-write |
| %hn | write low 2 bytes | partial-write |
| %hhn | write low byte | byte-write |
| %N$p | read the Nth arg | indexed read |
| %N$n | write to the Nth arg | indexed write |
