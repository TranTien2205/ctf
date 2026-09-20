---
name: rev-triage
description: >
  Reverse engineering router. Use when a binary, bytecode, managed assembly,
  packed sample or firmware image must be understood: identify, decompile, find
  the deciding check, replicate it. Routes to references/ for packer, crypto, VM
  and managed-code depth.
tags: [rev, reverse-engineering, decompiler, analysis]
environment: [ctf, lab]
---

# Reverse Engineering — Router

Goal: understand the logic well enough to produce the accepted input. Memory
corruption is a different job — use `../pwn-binary-triage/`.

## First probe

`file` and a targeted `strings` pass, before any decompiler. Together they answer
the only question that matters at this stage: is the accepted input compared
against something already in the binary, or computed at runtime?

**Falsifier** - the observation that closes this class: the binary's logic is not
the puzzle. If the goal is to corrupt memory rather than to understand a check,
this is `../pwn-binary-triage/`.

## Identify first

```bash
file ./bin
strings -n8 ./bin | grep -iE "flag|CTF\{|key|correct|wrong"
strings -e l ./bin | head          # UTF-16 strings
binwalk ./bin                      # embedded archives or filesystems
binwalk -E ./bin                   # entropy: a flat high curve means packed
```

Packed? `strings ./bin | grep -iE "upx|themida|vmprotect|aspack"`. UPX unpacks
with `upx -d ./bin`; anything else goes to `references/packer-analysis.md`.

## Dynamic before static

`ltrace ./bin` often exposes the comparison directly; `strace` shows the syscall
shape; `gdb` breaks on the check function. Run these before committing to a
decompile — they are minutes, not hours.

## Static

```bash
r2 -A ./bin
# afl              list functions
# pdf @sym.<name>  disassemble
# pdc @sym.<name>  pseudo-C
# axt @sym.<name>  cross references
# iz / izz         strings in data / everywhere
```

Read decompiled C, not raw hex. Misreading an offset or a loop stride is the most
common source of a wrong conclusion. If the pseudo-C is not good enough, install
a decompiler plugin or run Ghidra headless — verify the tool exists before
relying on it, and never report output from a tool that was not run.

Functions worth reading first: `main`, and anything named for the decision —
check, verify, validate, encrypt, decrypt, transform, win.

**Read the deciding function completely.** Leaving the most suspicious routine
unread while brute-forcing around it is the failure mode this router exists to
prevent.

## Common CTF shapes

- Input compared against a precomputed value: find the comparison, then either
  extract the expected value or replicate the computation in reverse.
- A short-key XOR loop, base64, a Caesar or substitution table →
  `references/crypto-recognition.md`.
- Anti-debug checks such as a ptrace self-attach or a debugger-present query:
  patch the check or preload a stub → `../ctf-reverse/anti-analysis.md`.

## Route to depth

| Finding | File |
|---|---|
| Packed or protected | `references/packer-analysis.md` |
| Crypto inside the binary | `references/crypto-recognition.md` |
| VM or bytecode obfuscation | `references/vm-analysis.md` |
| .NET or Java assembly | `references/managed-code.md` |
| Firmware or IoT image | `references/firmware-analysis.md` |
| Anything narrower | one named file in `../ctf-reverse/` |

## Discipline

- Trace before you decompile.
- Understand the check before writing a solver; if it can be inverted, do not
  brute-force it.
- Suspect a misread? Verify with a decompiler or a local replica rather than
  reasoning from the guess.
- A binary that takes input deserves a local replica so fuzzing costs nothing.
  See `../LOOP_DISCIPLINE.md`.
