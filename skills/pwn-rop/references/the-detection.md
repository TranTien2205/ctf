# Detecting the ROP case — when this skill applies


The skill applies when: IP control is proven AND NX is on AND the
exploit needs actions the bug alone can't express — calls, syscalls,
writes.

## The boundary test

- Shellcode can run (NX off or RWX): inject, don't chain.
- No IP control yet: the upstream class is the real one — return to
  pwn-stack-overflow or pwn-format-string.

## The decision

The triage's `nx: true` + your proven control = the ROP case.
