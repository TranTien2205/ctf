# The xref path — backwards from the verdict


The fastest route: find the verdict strings, read the xrefs TO them,
walk backwards to the compare.

    r2 -A ./chal
    iz                          # the strings
    axt @ str.wrong             # xrefs to the failure string
    pdf @ <the_func>            # disassemble it

## Why backwards

afl walks forwards through hundreds of functions; the verdict's xref
points at the exact function that decides.
