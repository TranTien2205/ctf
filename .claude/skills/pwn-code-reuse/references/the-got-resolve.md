# The GOT's states — resolved vs lazy


- Resolved (post-call or BIND_NOW): the real function's address.
- Lazy (pre-call): the resolver stub's address — a binary/ld address.

## The read

A GOT read post-call gives libc; pre-call gives the resolver stub —
know which state the entry is in.
