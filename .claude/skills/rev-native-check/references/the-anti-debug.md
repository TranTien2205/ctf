# Anti-debug — the ptrace checks


ptrace self-checks, timing checks: the binary detects the debugger —
the reads under r2 -d may show different behavior.

## The moves

- Patch the ptrace call (it's an import — find it in afl).
- Emulate the function instead of debugging it.
- Static-only: replicate without running.
