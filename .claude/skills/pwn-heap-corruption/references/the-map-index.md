# Heap reference map — the index


## Foundations
- glibc-version-first, chunk-anatomy, the-bins, first-fit,
  bin-map, alignment-16, alignment-x86, size-class-table,
  chunk-flags, the-link-field-offset, mmap-chunks, the-heap-init

## Version gates
- version-feature-map, safe-linking, tcache-key,
  the-consistency-checks, free-hook, vtable-check,
  the-security-checks family

## Bugs → primitives
- the-bug-shapes, primitive-matrix, uaf-primitive, double-free,
  off-by-one, index-array-bug, uninit-read, multi-chunk-overflow,
  heap-race, the-boundary-check

## Techniques
- tcache-poisoning, fastbin-dup, the-unsorted-write, unlink-macro,
  house-of-force, house-of-spirit, house-of-botcake,
  house-of-einherjar, house-of-mind, house-of-lore, house-of-water,
  house-of-roman, large-bin-attack, tcache-stash, overlapping-chunks,
  fake-chunk, prev-in-use-bit, prev-size-field

## Leaks
- unsorted-bin-leak, heap-leak, environ-leak, the-leak-types,
  libc-version-offsets, the-top-leak, the-null-scan, size-shrink

## Grooming
- heap-feng-shui, guard-chunks, the-free-order, coalesce-order,
  the-consolidate-window, malloc-consolidate, the-object-table,
  grooming-anti-frag, the-determinism, first-fit

## Endings
- write-targets-heap, fsop-basics, io-list-all, exit-handlers,
  system-binsh, one-gadget, the-exec-target family, the-endgame-table,
  the-flag-loc, the-flag-in-mem, the-flag-object, the-app-ptr,
  the-environ-write, the-dead-write

## Ops discipline
- menu-driver-map, the-add-op, the-edit-op, the-show-op,
  the-menu-free, the-alloc-lifecycle, the-write-count, the-order-of-work,
  bin-poison-verify, write-then-read-verify family, the-verified-run

## Diagnosis
- heap-crash-map, r2-heap-view, r2-breakpoints, troubleshoot,
  anti-patterns, the-trap-list

## Discipline
- workflow, detection, evidence, falsifiers, heap-notes,
  negative-results family, the-field-notes, the-checklist,
  the-glossary, the-map-index
