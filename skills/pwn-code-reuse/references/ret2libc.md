# ret2libc — calling into libc


The dynamic-binary path: ret into a libc function — system() the usual
target — with args from your chain.

## The recipe

    pop rdi ; "/bin/sh" addr
    ret                     # alignment
    system@libc

## Requirements

- A libc pointer to system — a leak (the resolved GOT entry or a
  known-offset computation).
- "/bin/sh" — the libc's own string (search it) or your planted bytes.

## Falsifier

The libc is unknown (no leak, no shipped file): addresses are
uncomputable — leak first or use the binary's own code.
