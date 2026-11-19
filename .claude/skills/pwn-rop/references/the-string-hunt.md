# Hunting strings — /bin/sh and friends


    strings -t x ./chal | grep -iE 'bin/sh|flag|/bin'

## The find

- `/bin/sh` in rodata: a fixed arg under non-PIE.
- `flag.txt` paths: the win function's target.
- Format strings: info about the program's prints.

## PIE

PIE: the string's address = base + its offset — needs the code leak.
