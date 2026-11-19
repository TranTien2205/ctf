# Decoding the program stream — deep

Companion to `vm-program-decode.md`.

The prog[] byte array decodes against the table — pc walks ops + immediates; a flag-checker is a read-transform-cmp chain.
