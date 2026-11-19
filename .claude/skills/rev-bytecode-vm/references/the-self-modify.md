# Self-modifying programs — the falsifier case

Some CTF VMs mutate the program array mid-execution — the byte
stream at rest ISN'T the stream at pc=N.

## The consequence

Static decode gives the INITIAL program — not the running one. The
falsifier trips: the dispatch or program is runtime-generated.

## The route

Trace: run the VM, log the stream as executed — the dynamic path
reveals the real program.
