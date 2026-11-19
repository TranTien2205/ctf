# Reading a size — the leak from metadata


Reading a chunk's size word leaks nothing directly — but reading fd/bk
leaks pointers; the useful fields are the LINK fields, not the size.

## Reminder

The leak is in the links — the size word is corruption target, not
leak source (except for layout inference).
