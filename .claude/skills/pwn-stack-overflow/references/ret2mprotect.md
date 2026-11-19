# ret2mprotect — make the stack executable

Can't disable NX but can call mprotect: mark a region RWX, then write and jump to shellcode there.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX on, mprotect@plt or in libc | mprotect callable | mprotect the buffer |
| shellcode written to a known buffer | then jump | two stages |

## Steps

1. Need mprotect@plt (or libc mprotect via a leak).
2. chain: pop rdi(buf) + pop rsi(len) + pop rdx(7=rwx) + mprotect@plt + read@plt(stage2) + jmp buf.
3. Stage 2 writes the shellcode to the now-executable buffer and jumps.
4. Alternatively: ret2dlresolve or a one-shot execve.

## Falsifier

Falsifier — mprotect not reachable (no PLT, no leak): can't make a region RWX — stick to ROP/syscall chains.

## Traps

- mprotect(addr, len, PROT_READ|WRITE|EXEC=7).
- The buffer must be page-aligned for mprotect — use the page base.
- A simpler alternative under some stacks: call mmap for a fresh RWX region.

## Commands

```bash
readelf -s ./chal | grep -iE 'mprotect|mmap'
```

## Cross-references

`ret2shellcode.md` · `rop-basics.md`
