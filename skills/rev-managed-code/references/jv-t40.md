# The JVM check detail 40

A Java flag-check detail — read the bytecode around the deciding if_*.

## The route

Locate the deciding compare, read the ops feeding it, extract the expected, invert the transform, verify on the real binary. A decompile never analyzed is recon.
