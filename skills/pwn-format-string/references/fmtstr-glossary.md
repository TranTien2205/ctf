# Format-string glossary


| Term | Meaning |
|---|---|
| %p / %x | read an arg as a hex pointer/word |
| %s | deref an arg as a char* string |
| %n | write the chars-printed count to an arg's pointee |
| %hhn / %hn | byte / short-width %n write |
| %N$ | direct access to the Nth vararg |
| %Nc | print N chars — count padding for %n |
| arg offset N | which vararg slot your input lands at |
| marker | planted bytes (AAAA) located in the dump |
| the count | cumulative chars printed before a specifier |
| plant | placing a pointer at a %N$ position |
| the redirect | the pointer-write's firing (call/return/free) |
| one-shot | a single format call; the whole exploit in one payload |
| blind fmtstr | no output channel — crash is the only signal |

| %N$hn / %N$hhn | the positional form of the write |
| saved_ret | the function's saved return address — a write slot |
| the arg window | the range of varargs printf can address |
| a dead write | a write whose slot is never dereferenced |
| the marker scan | sweeping %N$p to locate your input's arg position |
| the runbook | detect, offset, leak, plant, write, verify, fire |
| an import slot | a GOT entry — a fixed write target (partial RELRO) |
| %a %e %g | float specifiers — an alternative read form |
| FORTIFY %n-off | %n disabled by hardening — read-only fmtstr |
| the ledger | the running byte-count for a multi-write plan |
