# The padding — reaching the rip slot


The padding's length = offset to saved_rip — measured by pwn_cyclic,
not guessed:

    python3 tools/pwn_cyclic.py 300            # the pattern
    # crash; note the rip value
    python3 tools/pwn_cyclic.py --find 0x6161.. # the offset

## Falsifier

The offset isn't verified: the chain's start is unknown — measure.
