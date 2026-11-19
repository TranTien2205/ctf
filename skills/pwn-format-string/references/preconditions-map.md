# Preconditions — what must be true — map

Companion to `preconditions.md`.

| For | Must be true |
|---|---|
| the class | your input is the format argument |
| %p leak | the output is reflected |
| %s arb-read | a pointer you control at a %N$s position |
| %n arb-write | a pointer you control at a %N$n position |
| GOT overwrite | partial RELRO |
| ret-addr | the stack addr is leaked/known |
| __free_hook | glibc ≤ 2.34 |
| the offset | your input is a printf argument |
| the write | the count reaches the needed value |
