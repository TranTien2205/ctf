# Heap corruption — the one-paragraph summary


The bug gives a primitive (UAF/dup/overflow/oob). The glibc version
picks the technique family (tcache/fastbin/dup/poison/house-of). Leaks
feed the aims (libc/heap/stack in that order on modern glibc). The
corruption lands in a bin or a size field; the allocator's own
machinery delivers the write; the write lands on a call slot that
fires. The discipline: version first, leak before write, verify every
stage independently, and read the abort messages as diagnostics.
