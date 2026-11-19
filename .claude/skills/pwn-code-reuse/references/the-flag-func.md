# The flag function — verifying it reads the flag


A function named like a win func may need args, may check state, may
just print a decoy — verify its disassembly before chaining.

## The check

    r2 -A ./chal ; pdf @ <func>
    strings around its code — does it open flag.txt?

## Falsifier

It doesn't read the flag: a real call must be built.
