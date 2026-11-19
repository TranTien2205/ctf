# The full SROP recipe — every register — checklist

Companion to `the-srop-full.md`.

## Checklist

- [ ] 1. rax = 15 (rt_sigreturn) — via pop rax or a sigreturn-imp import.
- [ ] 2. syscall gadget — fires the frame load.
- [ ] 3. The 248-byte frame follows on the stack — every register set.
- [ ] 4. rip in the frame = your next gadget; rdi/rsi/rdx = the args.
