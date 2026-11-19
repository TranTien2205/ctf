# Common mistakes — the expensive ones

## Offset and layout

- Off-by-one at the frame edge: offset to saved RIP vs to saved RBP
  differs by 8 on x64.
- Assuming -fomit-frame-pointer is off: it often isn't; measure.
- Writing past the canary — a smashing write trips __stack_chk_fail
  BEFORE your RIP lands.

## Chain construction

- Arguments on the stack for x64: args go in registers via pop gadgets;
  stack-args is the x86 (32-bit) layout.
- A 'pop rdi; ret' consumes the NEXT qword — fill it with the arg, then
  the next address follows.
- Missing 'pop rdx': the classic hole — find it via mov rdx or ret2csu.

## Protections

- Confusing NX with ASLR: NX is 'stack isn't executable'; ASLR is
  'addresses move'. Both are independent.
- Assuming __stack_chk_fail in a static binary's imports means canary is
  enabled — read the %fs:0x28 load.

## The read

- Banned bytes in addresses: \x00 in a ROP address through scanf/fgets
  terminates input early.
- Newline-terminated reads need the trailing \n on the payload.

## Evidence

- A segfault without register inspection is not control.
- 'RIP = 0x41...' proves control; 'crash at input' proves only a crash.
