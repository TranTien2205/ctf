# The offset first — the chain's anchor


Every chain starts at the saved-return slot — the padding length is
measured, not guessed:

    python3 tools/pwn_cyclic.py 300        # emit the pattern
    # feed it, note the rip value at the crash
    python3 tools/pwn_cyclic.py --find 0x61616c61   # the offset

## Falsifier

The offset isn't verified — the chain's start is unknown; everything
else is speculation.
