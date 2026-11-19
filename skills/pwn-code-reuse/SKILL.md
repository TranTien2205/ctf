---
name: pwn-code-reuse
description: >
  Action-oriented depth skill for ROP and code reuse. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: pwn-stack-overflow, pwn-format-string.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [pwn, pwn-code-reuse, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# ROP and code reuse

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

this class presupposes control of the instruction pointer, so confirm that first; then read the protections to decide whether a leak is needed at all, and build the leak chain and verify the leaked value looks like a libc address before chaining further

**Falsifier** — the observation that closes this class: the gadgets present cannot express the call -- no controllable argument register, or no writable page to pivot into -- which tools/pwn_triage.py reports from the executable segments it actually scanned, since ROPgadget and ropper are absent here
## Recognise

This class presupposes control of the instruction pointer — a confirmed stack
or format-string overwrite — with NX on, so the payload is borrowed code, not
injected code.

## Confirm

Read the protection sheet `tools/pwn_triage.py` already produced: PIE or ASLR
decides whether a leak is needed at all, RELRO decides whether GOT is a
reachable write, and its gadget report names what the binary can express.

| Shape | Route |
|---|---|
| dynamic binary, libc supplied or leakable | ret2libc — `system`, `execve` gadgets |
| static binary | syscall gadgets or `int 0x80` |
| no `pop rdi` but `__libc_csu_init` present | ret2csu — the universal call primitive |
| write what/where needed | GOT entry, `.data`, or a `read` into a writable page |

Confirmation is the target action observed — a shell prompt, a read of the flag
path — never a clean exit after the chain.

## Traps

- On x86-64 a `ret` gadget before the final call fixes stack alignment; a chain
  that crashes inside `system` on `movaps` is an alignment bug, not a bad chain.
- The remote libc must match — leak a resolved symbol and identify the version
  (`tools/gadget_lookup.py`, libc database) before hard-coding offsets.
- `ROPgadget`/`ropper` are absent here; `r2 /R` and the `pwn_triage.py` gadget
  report are the local answer.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal      # protections + gadgets in one report
r2 -c "/R pop rdi" ./chal
```

## Routing

Shares signals with: `../pwn-stack-overflow/`, `../pwn-format-string/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/pwn-rop/references/rop-chains.md`
- `skills/pwn-rop/references/ret2libc.md`
- `skills/ctf-pwn/rop-and-shellcode.md`

| Any ROP/code-reuse question | `references/gadget-selection.md` |

### Reference corpus (under `references/`)

The corpus is topic-based; each topic has a base file plus `-deep`,
`-checklist`, and `-map` companions.

**Foundations and workflow**

- `references/workflow.md` — the whole run in order: control → protections → leak → chain → verify → fire
- `references/detection.md` — when this class applies (IP control + NX)
- `references/the-prerequisite.md`, `references/nx-forces-reuse.md`, `references/gadget-anatomy.md`, `references/the-chain-shape.md`
- `references/the-frame-layout.md`, `references/the-64-vs-32.md`, `references/the-x64-frame.md`, `references/the-stack-view.md`
- `references/the-theory.md` — why borrowing works: the stack is the program
- `references/the-route-map.md`, `references/the-dispatch.md`, `references/the-ending-choice.md`

**Gadgets**

- `references/pop-gadgets.md`, `references/ret-gadget.md`, `references/the-call-gadget.md`, `references/syscall-gadgets.md`, `references/the-xor-zero.md`
- `references/the-gadget-scan.md`, `references/the-gadget-hunt.md`, `references/the-gadget-search.md`, `references/the-scan-order.md`, `references/the-raw-gadgets.md`
- `references/the-side-effects.md`, `references/the-side-effects-2.md`, `references/the-tail-check.md`, `references/the-clobber.md`, `references/the-gadget-verify.md`
- `references/the-pair-pop.md`, `references/the-extra-pops.md`, `references/the-long-tail.md`, `references/the-reg-sub.md`, `references/the-pop-all.md`, `references/the-gadget-dup.md`, `references/the-gadget-rank.md`
- `references/the-libc-gadgets.md`, `references/the-gadget-classes.md`, `references/the-conditional.md`, `references/the-call-gadget-2.md`

**Recipes — the named chains**

- `references/the-minimal-chain.md`, `references/the-chain-complete.md`, `references/the-recipes-index.md`, `references/the-recipes2.md`
- `references/the-ret2win.md`, `references/the-win-check.md`, `references/the-flag-func.md`, `references/the-win-function.md`
- `references/the-system-chain.md`, `references/the-execve-chain.md`, `references/the-leak-chain.md`, `references/the-write-chain.md`, `references/the-read-chain.md`
- `references/ret2libc.md`, `references/ret2csu.md`, `references/the-csu-pops.md`, `references/the-csu-recipe.md`
- `references/the-srop.md`, `references/the-srop-full.md`, `references/the-sig-return.md`
- `references/the-ret2dl.md`, `references/the-rela-entry.md`, `references/the-sym-entry.md`, `references/the-version-tag.md`, `references/the-verneed.md`, `references/the-linkmap.md`, `references/the-dynamic-tag.md`
- `references/mprotect-chain.md`, `references/the-mmap-chain.md`, `references/the-mmap-variant.md`, `references/the-brk-syscall.md`
- `references/the-one-gadget-2.md`, `references/the-one-gadget-2.md`, `references/the-ret2plt.md`, `references/the-stub-call.md`, `references/the-ret2any.md`

**Leaks**

- `references/leak-the-got.md`, `references/the-got-read.md`, `references/the-print-path.md`, `references/the-leak-shape.md`
- `references/the-lazy-binding.md`, `references/the-lazy-got.md`, `references/the-got-resolve.md`, `references/the-got-table.md`
- `references/the-libc-id.md`, `references/the-remote-leak.md`, `references/the-crosscheck-leak.md`, `references/the-leak-recheck.md`
- `references/the-stack-leak.md`, `references/the-env-ptr.md`, `references/the-canary-leak.md`, `references/the-early-leak.md`
- `references/the-leak-ladder.md`, `references/the-order-of-leaks.md`, `references/the-leak-then.md`, `references/the-base-math.md`

**Pivots and staging**

- `references/the-pivot.md`, `references/the-fp-pivot.md`, `references/the-pop-rsp.md`, `references/the-xchg-pivot.md`, `references/the-stack-skip.md`, `references/the-esp-pivot.md`, `references/the-double-pivot.md`, `references/the-fake-frame.md`, `references/the-fp-chain.md`
- `references/the-second-stage.md`, `references/the-stdin-path.md`, `references/the-stage-alloc.md`, `references/the-return-loop.md`, `references/the-chain-in-parts.md`, `references/the-heap-chain.md`, `references/the-two-stage.md`, `references/the-second-over.md`, `references/the-strncpy-gadget.md`, `references/the-fgets-path.md`

**Protections and boundaries**

- `references/partial-vs-full-relro.md`, `references/pie-and-rop.md`, `references/canary-rop.md`, `references/the-protections-map.md`, `references/the-canary-slot.md`
- `references/the-boundary.md`, `references/the-dynamic-binary.md`, `references/the-static-binary.md`, `references/the-no-import.md`, `references/the-remote-diff.md`

**Composition and targets**

- `references/the-format-combo.md`, `references/the-heap-combo.md`, `references/the-direct-write.md`
- `references/the-binsh-plant.md`, `references/the-bss-wr.md`, `references/the-got-entry.md`, `references/the-plt-vs-got.md`, `references/the-two-addr.md`
- `references/the-write-slot.md`, `references/the-write-primitive.md`, `references/the-read-primitive.md`, `references/the-multi-write.md`, `references/the-second-write.md`
- `references/the-init-fini.md`, `references/the-tls-dtor.md`, `references/the-atexit-list.md`, `references/the-dtor-slot.md`, `references/the-vtable-call.md`, `references/the-libc-start.md`
- `references/the-hybrid.md`, `references/the-shellcode-hybrid.md`, `references/the-multiplex.md`, `references/the-double-call.md`, `references/the-sub-call.md`, `references/the-call-depth.md`

**Discipline**

- `references/evidence.md`, `references/falsifiers.md`, `references/troubleshoot.md`, `references/anti-patterns.md`, `references/the-traps-table.md`, `references/the-false-signal.md`
- `references/the-chain-verify.md`, `references/the-first-fail.md`, `references/the-checkpoint.md`, `references/the-verify-table.md`, `references/the-order-of-checks.md`, `references/the-rip-verify.md`, `references/the-arg-check.md`, `references/the-arg-echo.md`, `references/the-miss.md`, `references/the-wrong-offset.md`, `references/the-call-verify.md`, `references/the-verify-final.md`, `references/the-verify-end.md`, `references/the-recheck-loop.md`, `references/the-probe-chain.md`, `references/the-replay.md`
- `references/the-checklist.md`, `references/the-checks-list.md`, `references/the-build-order.md`, `references/the-order-wrong.md`, `references/the-order-notes.md`, `references/the-partial-order.md`
- `references/the-e2e.md`, `references/the-field-notes.md`, `references/the-field-again.md`, `references/the-notes-take.md`, `references/the-chain-doc.md`, `references/the-chain-craft.md`
- `references/the-glossary.md`, `references/the-map-index.md`, `references/the-final-map.md`, `references/the-summary-cr.md`, `references/the-summary-end.md`, `references/the-map-close.md`

**Argument passing**

- `references/the-arg-set.md`, `references/the-arg-order.md`, `references/the-arg-sets.md`, `references/the-arg-preload.md`, `references/the-regs-table.md`, `references/the-syscall-args.md`, `references/the-syscall-map.md`, `references/the-multi-arg.md`, `references/the-stack-arg.md`, `references/the-32bit-args.md`, `references/the-stack-data.md`, `references/the-register-preserve.md`, `references/the-x64-reg.md`

**Alignment, bytes and transport**

- `references/the-align-fix.md`, `references/the-align-fix.md`, `references/the-ret-sled.md`, `references/the-alignment-crash.md`
- `references/the-null-byte.md`, `references/the-newline.md`, `references/the-pack-fmt.md`, `references/the-64bit-pad.md`, `references/the-send-path.md`, `references/the-comm.md`

**Hooks, endings, misc**

- `references/the-exit-ending.md`, `references/the-endloop.md`, `references/the-crash-clean.md`, `references/the-ret-chain-end.md`, `references/the-chain-end.md`, `references/the-end-map.md`, `references/the-end-choice.md`, `references/the-order-of-ends.md`, `references/the-flag-end.md`, `references/the-flag-path.md`
- `references/the-sleep-reuse.md`, `references/the-strcmp-oracle.md`, `references/the-side-channel.md`, `references/the-atoi-gadget.md`, `references/the-realloc-misc.md`, `references/the-sprintf-write.md`, `references/the-fwrite-gadget.md`, `references/the-setbuf-gadget.md`, `references/the-jmp-table.md`
- `references/the-rpath.md`, `references/the-soname.md`, `references/the-fp-state.md`, `references/the-noncritical.md`, `references/the-stack-fence.md`, `references/the-rsp-guard.md`, `references/the-rsp-clean.md`, `references/the-ret-fall.md`, `references/the-bounds.md`, `references/the-chain-len.md`, `references/the-pad-end.md`, `references/the-pad-to-ret.md`, `references/the-offset-slots.md`, `references/the-saved-rip.md`, `references/the-frame-ptr.md`, `references/the-fp-vs-sp.md`, `references/the-stack-var.md`, `references/the-stack-tgt.md`, `references/the-offset-find.md`, `references/the-offset-math.md`, `references/the-absolute.md`, `references/the-addr-scheme.md`, `references/the-const-offsets.md`, `references/the-symbol-tables.md`, `references/the-import-list.md`, `references/the-import-funcs.md`, `references/the-plt-index.md`, `references/the-plt-stub.md`, `references/the-plt-targets.md`, `references/the-func-table.md`, `references/the-call-shapes.md`, `references/the-real-call.md`, `references/the-call-args.md`, `references/the-call-return.md`, `references/the-call-chain.md`, `references/the-sig-check.md`, `references/the-scope-dead.md`, `references/the-dead-end.md`, `references/the-late-call.md`, `references/the-multi-chain.md`, `references/the-turbo-rop.md`, `references/the-end-check.md`, `references/the-sigma.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
