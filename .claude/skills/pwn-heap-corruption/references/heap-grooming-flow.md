# The grooming flow — alloc/free as bytecode


Think of alloc/free ops as instructions:

    A=alloc(0x90) B=alloc(0x90) C=alloc(0x90)
    free(B) free(A)          # holes: A | [B] | C
    D=alloc(0x90)            # D reuses... depends on bin
    # state: deterministic if you scripted it

## The discipline

- Write the sequence first; run it second.
- Annotate each op with the bin state it leaves.
- Verify with dmh at checkpoints.

## Falsifier

The ops aren't scriptable (interactive-only binary): r2 -d to observe,
or pipe scripted input — interactivity isn't a blocker.
