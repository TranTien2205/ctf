# Crypto recognition

Routing module for `rev-triage`. The pipeline is identify, decompile, find the deciding check, replicate it - this file is one named step or artifact; it never analyzes for you.

Constant tables (AES S-boxes, SHA K-constants, RC4
patterns), math shapes (bignum, EC points) - crypto-
recognition.md names what the constants mean before
assuming custom crypto.

## Pivot

Module read -> the depth file or sibling module the artifact names.
