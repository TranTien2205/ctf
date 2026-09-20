---
name: pwn-binary-triage
description: >
  Binary exploitation router for authorized CTF challenges. Use when an ELF or PE
  takes input and the goal is memory corruption. Identify the protections, prove
  control of the instruction pointer, then open exactly one depth file.
tags: [ctf, pwn, binary, memory-corruption]
environment: [ctf, lab]
---

# Binary Exploitation — Router

Goal: turn an input into control of execution. If the binary only has to be
*understood* — a licence check, an encoded flag, a VM — that is reversing, and
`../rev-triage/` is the right router.

This file routes. Open one depth file from the table, never the directory.

## First probe

Two commands, before any payload. They decide the row you take.

```bash
file ./chal && checksec --file=./chal     # arch, RELRO, canary, NX, PIE
python3 -c "print('A'*200)" | ./chal      # does it crash, and where
```

If it crashes, get the exact offset before anything else — never by trying
lengths one at a time:

```bash
python3 -c "from pwn import *; print(cyclic(200).decode())" | ./chal
# read the faulting value out of the core or the debugger, then:
python3 -c "from pwn import *; print(cyclic_find(0x6161616c))"
```

**Falsifier** — the observation that closes this class: the input never reaches a
memory-unsafe operation. The length is validated, the read is bounded, and what
looked like a crash is a handled error or a clean exit. Go back to
`../rev-triage/`.

## Route to depth

| Finding | File |
|---|---|
| Stack overflow, offset known, no mitigation to defeat yet | `../ctf-pwn/overflow-basics.md` |
| NX on and no PIE: code reuse required | `../pwn-rop/SKILL.md` |
| NX on with PIE or ASLR: a leak is needed first | `../pwn-rop/references/ret2libc.md` |
| A longer chain, sigreturn, or stack pivot | `../ctf-pwn/rop-advanced.md` |
| A format specifier reaches `printf` with user data | `../ctf-pwn/format-string.md` |
| `malloc`/`free` on user-sized chunks, double free, use-after-free | `../ctf-pwn/heap-techniques.md` |
| Heap chain that needs a file-structure primitive | `../ctf-pwn/heap-fsop.md` |
| A kernel module, a driver, or a supplied `bzImage` | `../ctf-pwn/kernel.md` |
| `seccomp` is on, or the shell is blocked | `../ctf-pwn/sandbox-escape.md` |
| Shellcode is accepted and the page is executable | `../ctf-pwn/rop-and-shellcode.md` |
| Nothing above fits | `../ctf-pwn/advanced-exploits.md`, one file at a time |

Full technique depth is in `../ctf-pwn/`; its `SKILL.md` indexes every file in
that directory. That whole corpus is behind a manual gate — reach it from a named
row above, not by browsing.

## Discipline

- Prove instruction-pointer control before building any chain. A crash is not
  control; a controlled value in the saved return address is.
- One mechanism at a time. Five probes or fifteen minutes per mechanism, then
  park at priority 0 with `tools/state.py --deprioritize` and change layer —
  never a sixth payload variant of the same idea.
- Match the libc before trusting any offset. An offset from the wrong libc
  produces a crash that looks like a bug in your chain.
- Work locally first. Only move to the remote target once the exploit is
  reproducible against the supplied binary.
- Budget and escalation as in `../LOOP_DISCIPLINE.md`.
