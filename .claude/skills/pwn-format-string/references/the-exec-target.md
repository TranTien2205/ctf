# Choosing the exec target — system vs execve vs a win func


The redirect's landing point: a win function (easiest), system (needs a
string arg), or a syscall stub (needs regs set).

## Decision

- a win/flag function exists — direct — write its addr.
- system imported/leaked — needs '/bin/sh' arg — check the call-site arg.
- syscall gadget — execve via regs — needs reg control.

## Falsifier

No suitable landing target exists at a reachable address. Check the
call-site's arg before choosing system.
