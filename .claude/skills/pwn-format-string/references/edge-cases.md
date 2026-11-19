# Edge cases — the odd shapes

| Shape | Handling |
|---|---|
| the fmt is a static const | reachable another way? |
| input upper/lower-cased | specifiers are case-sensitive |
| output hex-only | %p leak fine; %s bytes may filter |
| recursive fmtstr call | the offset shifts per call |
| fmt in a loop | offset stable; leak re-reads |
| input split across two calls | specifiers span both |
| fmt is also a smash path | fmtstr leaks, smash exploits |
