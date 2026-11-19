# The gadget soup — reading raw /R output


`/R` output is a list of address: instruction-sequence lines — parse
the tail (everything to the ret), not the first mnemonic.

## The parse

A gadget "pop rdi" may have more instructions — the full listing is
the truth.
