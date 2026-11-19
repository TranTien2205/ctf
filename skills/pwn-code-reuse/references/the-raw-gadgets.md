# The raw gadget list — the essential set


The set pwn_triage --gadgets reports (when present):

- pop rdi/rsi/rdx/rax — the setters.
- syscall — the kernel entry.
- ret — the aligner.
- leave; ret — the pivot.
- mov-store — the write.

If any are absent, the substitute notes name the workaround.
