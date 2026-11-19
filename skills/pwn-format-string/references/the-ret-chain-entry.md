# Where the chain begins — the write's landing point


The %n write lands the chain's FIRST address: a gadget or function that
execution next reaches. Everything after that address is a normal
ROP/call chain.

## Entry shapes

- → `pop rdi; ret` + args → ROP continues.
- → `system` / `execve-stub` → direct.
- → a function that prints the flag → done.

## Falsifier

The written address doesn't exist or crashes instantly: verify the
target's existence before writing.
