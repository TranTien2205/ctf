# The heap-corruption workflow — the whole run in order


1. Triage: pwn_triage ./chal — protections and the dangerous imports.
2. Version: name the glibc (shipped libc / base image / leak).
3. Map: the alloc lifecycle — sizes, counts, who frees what when.
4. Primitive: what the bug actually gives — UAF, double-free, overflow,
   index-OOB, dangling pointer.
5. Leak: unsorted-bin fd (libc), then environ (stack), then heap (fd
   de-mangle) as needed by the version.
6. Corrupt: the technique the version allows — tcache poison, dup,
   consolidate-overlap, largebin write, FSOP.
7. Redirect: the write's target — hook (<=2.34), FILE vtable, app
   pointer.
8. Verify the overlap/write before firing; land; pre-flag the bytes.

## The runbook kernel

    version → primitive → leak → corrupt → write → fire
