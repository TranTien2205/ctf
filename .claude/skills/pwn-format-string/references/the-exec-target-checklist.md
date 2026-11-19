# Choosing the exec target — system vs execve vs a win func — checklist

Companion to `the-exec-target.md`.

## Checklist

- [ ] a win/flag function exists — direct — write its addr.
- [ ] system imported/leaked — needs '/bin/sh' arg — check the call-site arg.
- [ ] syscall gadget — execve via regs — needs reg control.
