# The short-flag brute — when inversion fails

If the transform isn't invertible but the alphabet is small, brute
the checked bytes:

    for c in alphabet: run_vm(candidate + c) → check first fail pos

The VM's early-exit (fail at first wrong byte) is a byte-by-byte
oracle — each position independently bruteable.
