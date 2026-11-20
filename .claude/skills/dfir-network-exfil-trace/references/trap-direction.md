# Trap: Reading <- as sent

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`conv,tcp` prints B-to-A (`<-`) bytes BEFORE A-to-B (`->`). Measured fixture row: `20 1,880 bytes` then `20 9,080 bytes` — the 9,080 is A->B. Reading the first column as 'sent' inverts every exfiltration answer in the report. The ONLY defence: quote the row with its header and say which pair you read.

## Defence

Quote the row with the headers/markers that disambiguate it, and say which
field/direction produced the number. When two readings are possible, quote
enough context that only one survives.

## Related

`../SKILL.md` Traps section carries the class-level list; this module is the
single-trap long form.
