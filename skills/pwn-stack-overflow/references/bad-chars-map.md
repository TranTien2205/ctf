# Bad characters — which bytes the input path strips — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| scanf %s stops at whitespace | \x20\x09\x0a\x0b\x0d banned | avoid them |
| fgets stops at newline | \x0a banned | no newline bytes |
| read(n) raw | no byte filter | any bytes OK |
| input goes through a filter/validator | custom banned set | enumerate it |

## Falsifier

Falsifier — a needed address/opcode contains a banned byte and no equivalent exists: the chain must be reworked or the class is wrong.
