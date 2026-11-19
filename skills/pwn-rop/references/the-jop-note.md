# JOP — jump-oriented programming


When ret gadgets are scarce but jumps aren't: jmp-terminated
gadgets chained through a dispatcher gadget — the advanced variant.

## The dispatcher

`add rsp, X; jmp [reg]`-shaped sequences — rare; try ret gadgets
first via the substitutes.
