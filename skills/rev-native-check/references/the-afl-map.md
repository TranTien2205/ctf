# The afl map — the function inventory


    r2 -A ./chal ; afl

Every function: sym.imp.* (imports), sym.* (runtime), fcn.*/loc.*
(the binary's own).

## The interesting rows

- main — the usual check's home.
- Names matching check|verify|flag|password|valid — the candidate.
- sym.imp.strcmp|memcmp|strncmp — the compare calls.
