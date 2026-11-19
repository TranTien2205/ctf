# When the arg is in a register already


A redirect landing where a register already holds your string/address
— no pop gadget needed: the register's existing value is the argument.

## Check

At the redirect point, what does rdi/rsi already hold? If it's your
input buffer or a useful pointer, skip the pops.

## Falsifier

The register holds something unusable: set it explicitly with a pop.
