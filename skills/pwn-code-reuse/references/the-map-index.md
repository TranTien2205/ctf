# Code-reuse reference map — the index


## Foundations
- the-prerequisite, nx-forces-reuse, gadget-anatomy, the-chain-shape,
  the-frame-layout, the-64-vs-32, the-x64-frame

## Gadgets
- pop-gadgets, ret-gadget, the-call-gadget, syscall-gadgets,
  the-xor-zero, gadget-minimal, the-gadget-scan, the-gadget-hunt,
  the-side-effects, the-tail-check, the-clobber, the-gadget-verify,
  the-pair-pop, the-extra-pops, the-long-tail, the-reg-sub,
  the-gadget-classes, the-raw-gadgets, the-libc-gadgets

## Recipes
- the-ret2win, the-system-chain, the-execve-chain, the-leak-chain,
  the-write-chain, the-read-chain, the-csu-pops, the-csu-recipe,
  the-srop, the-srop-full, ret2csu, ret2libc, the-ret2dl, the-one-gadget-2,
  mprotect-chain, the-mmap-chain, the-mmap-variant, the-brk-syscall,
  the-minimal-chain, the-chain-complete

## Leaks
- leak-the-got, the-got-read, the-print-path, the-leak-shape,
  the-lazy-binding, the-lazy-got, the-libc-id, the-remote-leak,
  the-crosscheck-leak, the-stack-leak, the-env-ptr, the-leak-ladder,
  the-order-of-leaks

## Pivots and staging
- the-pivot, the-fp-pivot, the-pop-rsp, the-xchg-pivot,
  the-stack-skip, the-esp-pivot, the-heap-chain, the-second-stage,
  the-stdin-path, the-stage-alloc, the-return-loop, the-chain-in-parts

## Boundaries
- partial-vs-full-relro, pie-and-rop, canary-rop, the-protections-map,
  the-route-map, the-boundary, the-dynamic-binary, the-static-binary,
  the-no-import, heap-rwx family

## Composition
- the-format-combo, the-heap-combo, the-double-call, the-multiplex,
  the-sub-call, the-hybrid, the-turbo-rop, the-ordering, the-direct-write

## Discipline
- workflow, detection, evidence, falsifiers, troubleshoot,
  anti-patterns, the-traps-table, the-chain-verify, the-first-fail,
  the-checkpoint, the-verify-table, the-order-of-checks, the-e2e,
  the-field-notes, the-glossary, the-map-index
