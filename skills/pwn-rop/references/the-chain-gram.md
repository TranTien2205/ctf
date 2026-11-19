# The chain grammar — the formal shape


    chain := pad (entry)*
    entry := gadget_addr | arg_value | call_target | ending
    pad := byte × offset

The grammar's only structure: alternating addresses and values, each
consumed by the ret before it.
