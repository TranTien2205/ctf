# Hunting call reg — the mid-chain call


    /R call

`call rax; <...>; ret`-shaped: calls the register's target and
continues — a call that doesn't end the chain.

## The use

Fire a function mid-chain, then the ret continues — two calls in one
chain without re-entering.
