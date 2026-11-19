# Where the args actually sit — the stack picture — checklist

Companion to `fmtstr-args-on-stack.md`.

## Checklist

- [ ] printf's FIRST arg is rdi (the format) — specifiers count varargs:
- [ ] %1$p=rsi ... %6$p=r9; %7$p+ = stack.
- [ ] Your input buffer lives on the stack → typically N≥7.
