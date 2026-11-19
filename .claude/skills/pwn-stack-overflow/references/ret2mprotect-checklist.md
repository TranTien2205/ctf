# ret2mprotect — make the stack executable — checklist

Can't disable NX but can call mprotect: mark a region RWX, then write and jump to shellcode there.

## Checklist

- [ ] Need mprotect@plt (or libc mprotect via a leak).
- [ ] chain: pop rdi(buf) + pop rsi(len) + pop rdx(7=rwx) + mprotect@plt + read@plt(stage2) + jmp buf.
- [ ] Stage 2 writes the shellcode to the now-executable buffer and jumps.
- [ ] Alternatively: ret2dlresolve or a one-shot execve.

## Abort conditions

- mprotect(addr, len, PROT_READ|WRITE|EXEC=7).
- The buffer must be page-aligned for mprotect — use the page base.
- A simpler alternative under some stacks: call mmap for a fresh RWX region.

## Falsifier

Falsifier — mprotect not reachable (no PLT, no leak): can't make a region RWX — stick to ROP/syscall chains.
