# The Dalvik check detail 24

A smali flag-check detail — the register ops around the if-* branch.

## The route

Locate the deciding compare, read the ops feeding it, extract the expected, invert the transform, verify on the real binary. A decompile never analyzed is recon.
