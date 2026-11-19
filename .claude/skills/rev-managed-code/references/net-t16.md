# The .NET check detail 16

A .NET flag-check detail — read the IL around the deciding compare.

## The route

Locate the deciding compare, read the ops feeding it, extract the expected, invert the transform, verify on the real binary. A decompile never analyzed is recon.
