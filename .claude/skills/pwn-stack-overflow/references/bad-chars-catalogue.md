# Bad characters — which bytes the input path strips — case catalogue

The read function's allowed byte set determines which shellcode/chain bytes are legal. A banned byte kills the exploit silently.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | scanf %s stops at whitespace | \x20\x09\x0a\x0b\x0d banned | avoid them |
| 2 | fgets stops at newline | \x0a banned | no newline bytes |
| 3 | read(n) raw | no byte filter | any bytes OK |
| 4 | input goes through a filter/validator | custom banned set | enumerate it |

## Falsifier

Falsifier — a needed address/opcode contains a banned byte and no equivalent exists: the chain must be reworked or the class is wrong.
