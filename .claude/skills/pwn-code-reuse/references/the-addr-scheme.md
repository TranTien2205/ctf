# The address scheme — PIE-relative vs absolute


Non-PIE: every address absolute — the chain's entries are constants.
PIE: every address = base + offset — the chain's entries are computed.

## The rule

Under PIE: leak a code pointer, compute the base, then every gadget
and function address derives.
