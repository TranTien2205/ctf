# Closing notes — the fmtstr shape


The format string is the rare primitive that reads AND writes through
one argument: a leak and an arbitrary write share one input. The whole
exploit is arg-position bookkeeping — which arg is your pointer, which
count is your value, which slot is your target.

The discipline: verify the offset, verify the plant, verify the count,
verify the write — then fire. A fmtstr exploit that skips a check fails
at that stage, not mysteriously.

The corpus covers: detection, offset discovery, stack/binary/libc leaks,
arbitrary read, arbitrary write at every width, GOT/ret/hook targets,
PIE/RELRO/canary interactions, one-shot and loop services, blind and
truncated channels, and composition with stack smashing.
