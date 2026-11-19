# Choosing the ending — the decision tree — map

Companion to `the-ending-choice.md`.

| What's available | The ending |
|---|---|
| a win/flag function | ret to it — simplest |
| libc leak + system | ret2libc system("/bin/sh") |
| syscall gadget + regs | execve("/bin/sh") by syscall |
| only a read primitive | plant stage 2, pivot |
| only a write | GOT/hook/pointer redirect |
| hooks exist (<=2.34) | __free_hook = system |
