# Anti-debug — the ptrace checks — checklist

Companion to `the-anti-debug.md`.

## Checklist

- [ ] Patch the ptrace call (it's an import — find it in afl).
- [ ] Emulate the function instead of debugging it.
- [ ] Static-only: replicate without running.
