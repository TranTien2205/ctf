# Binary Analysis - Initial Triage

## checksec Output Interpretation
```bash
checksec --file=./binary

RELRO         # Full RELRO = GOT read-only after startup (harder to overwrite)
Stack Canary  # Present = stack overflow needs to leak/bypass canary first
NX            # Enabled = no shellcode execution on stack (need ROP)
PIE           # Enabled = binary base address randomized (need leak)
```

## File Identification
```bash
file ./binary
# ELF 64-bit LSB executable, x86-64, dynamically linked
checksec ./binary
strings ./binary | grep -i flag
strings ./binary | head -50
```

## Static Analysis Workflow
```bash
# Function listing
objdump -d ./binary | grep -A 20 "main>:"
nm ./binary | grep " T "           # Exported/text symbols

# Ghidra/IDA for decompilation (GUI)
# radare2 for quick CLI analysis
r2 -A ./binary
[0x...]> afl                        # List functions
[0x...]> pdf @ main                 # Disassemble main
```

## Dynamic Analysis Setup
```bash
gdb ./binary
(gdb) info functions
(gdb) disassemble main
(gdb) break main
(gdb) run

# With pwndbg/gef/peda extensions for enhanced output
pip install pwndbg  # or gef
```

## Identifying Libc Version
```bash
ldd ./binary                        # Shows linked libc path
./binary_libc.so --version          # If libc provided separately

# Match to online database
# https://libc.blukat.me/  (upload libc, get exact version)
```

## Checking for Common Protections Missing
```bash
checksec --file=./binary
# If NX disabled → shellcode injection possible
# If no canary → simple buffer overflow to overwrite return address
# If no PIE → addresses are static, easier ROP
# If no RELRO → GOT overwrite possible
```

## Determining Exploitation Category
```
Stack-based overflow    → look for gets(), strcpy(), sprintf() with fixed buffer
Format string           → look for printf(user_input) without format specifier
Heap exploitation       → look for malloc/free patterns, use-after-free
Integer overflow        → look for size calculations before malloc
Race condition          → look for TOCTOU patterns, threading
```

## Quick Vulnerability Grep
```bash
objdump -d ./binary | grep -E "call.*gets|call.*strcpy|call.*sprintf|call.*system"
strings ./binary | grep -E "system|/bin/sh|execve"
```

## Remote Interaction Setup (pwntools)
```python
from pwn import *

# Local
p = process('./binary')

# Remote
p = remote('target.com', 1337)

# Context
context.binary = './binary'
context.arch = 'amd64'
context.log_level = 'debug'

p.interactive()
```
