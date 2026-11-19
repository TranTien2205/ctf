# Boundary cases — where the textbook breaks

| Boundary | Effect | Fix |
|---|---|---|
| 32-bit vs 64-bit | arg positions differ | x86 low N, x64 high N |
| the call is snprintf | bounded output | the write still works |
| output truncated | partial leak only | the write doesn't care |
| input capped | short fmtstr | positional args still work |
| blind output | no leak shown | write blind, find a channel |
| fmt is a wrapper | nested printf | open if it passes buf |
