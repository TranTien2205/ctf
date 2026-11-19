# Self-modifying code — the runtime-decoded check


The check's bytes are written at run time — the static disassembly
shows data, not instructions.

## The route

Dynamic: r2 -d, break after the decode, read the decoded compare —
or dump the decoded region for static analysis.
