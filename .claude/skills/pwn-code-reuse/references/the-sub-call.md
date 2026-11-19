# Sub-calls — functions inside the chain


A chain can call a helper that itself does work: a function that
reads input, a function that allocates — sub-calls are just chain
entries whose "return" is the next entry.

## The rule

The called function's return address is the NEXT stack qword — it
continues the chain.
