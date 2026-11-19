# rbp vs rsp — the two stack registers


- rsp: the chain's walk pointer — ret reads [rsp].
- rbp: the frame pointer — only the leave;ret pivot uses it.

## The confusion

Corrupting rbp without a pivot does nothing for the chain; corrupting
rsp IS the pivot.
