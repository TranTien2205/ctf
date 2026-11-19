# Debugging the chain — the systematic walk


The bisect: verify each entry in order —

1. rip = gadget 1? → the overwrite's right.
2. The register = the arg? → the pop's right.
3. The call reached? → the alignment and the walk.
4. The call's args? → the pops' order and values.
5. The observable? → the call's semantics.

The first failing check is the bug's address.
