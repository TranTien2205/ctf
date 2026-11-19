# Choosing the GOT entry — the firing one


The GOT overwrite's entry must be a function the program calls AFTER
the write — a dead import's slot never fires.

## The find

Which imports are called after your write point? Trace the code path
— that import's GOT slot is the target.
