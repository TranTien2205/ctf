# Common mistakes — the expensive ones

## The offset
- N wrong because args 1-6 are registers on x64 — your input is at high N.
- N shifts with the call's frame depth — measure per call site.

## The write
- %n writes the count, not the pointer — the pointer is the arg.
- Forgetting the cumulative count — each %n sees all printed bytes.
- %hhn writes count&0xff — the LOW byte is what lands.

## The target
- A GOT write under full RELRO fails silently — check RELRO first.
- A ret-addr write needs the stack address — leak it.
- __free_hook only exists on glibc ≤2.34.

## Evidence
- A reflected pointer run is a leak, not control — it feeds the write.
- A write that doesn't redirect isn't execution — the target must fire.
