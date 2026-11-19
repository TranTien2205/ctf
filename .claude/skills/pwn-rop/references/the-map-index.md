# ROP reference map — the corpus index


## Builder and modes
- the-builder, the-ret2func-mode, the-syscall-mode, the-ret2plt-mode,
  the-pack-struct, the-script, the-chain-script, the-pwntools-port

## Anatomy
- the-offset-first, the-chain-layout, the-arg-order, the-binsh-source,
  the-ending, the-chain-bounds, the-bad-bytes, the-delivery

## Stages and leaks
- the-leak-stage, the-stage-two, the-reentry, the-two-stage-full,
  the-got-read, the-plt-resolve, the-leak-verify, the-offset-math,
  the-remote-libc, the-pie-leak, the-no-pie

## Recipes
- the-execve-chain, the-system-chain, the-mprotect-chain,
  the-ret2csu-build, the-srop-build, the-write-gadget,
  the-read-stage, the-pivot-build, the-got-overwrite, the-hook-ends,
  the-ret2dlresolve, the-win-call, the-fork-stage

## Gadgets
- the-gadget-feed, the-gadget-map, the-radare-scan, the-gadget-tail,
  the-missing-gadget, the-registers-x64, the-stack-args-x86

## Alignment and debug
- the-alignment, the-align-count, the-alignment-math,
  the-verify-chain, the-r2-debug, the-crash-triage, the-verify-stage,
  the-chain-debug, the-order-entry, the-final-walk, the-sendloop

## Discipline
- the-detection, the-workflow, the-evidence, the-falsifiers,
  the-checklist, the-chain-card, the-attempt-budget, the-partial-order,
  the-two-overflows, the-buffer-echo, the-stack-sprawl, the-one-shot,
  the-multi-call, the-jop-note, the-cop-note, the-map-index
