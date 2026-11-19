# Code-reuse anti-patterns — the ways runs die


- Building the whole chain before verifying the first gadget.
- Using gadget addresses from a different binary/libc build.
- Forgetting the alignment ret and debugging the "crash" for an hour.
- Hardcoding a libc offset without identifying the version.
- Calling got[x]'s contents instead of plt[x]'s stub.
- Passing "/bin/sh" that doesn't exist in memory.
- Writing the chain where the input's encoding mangles it.
- Assuming a pop gadget exists because a tutorial had it.
- Confusing the saved-rbp slot with the saved-rip slot.
- Treating a clean exit as success — the call must be observed.
