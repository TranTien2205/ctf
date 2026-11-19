# The verified run — the dry-run discipline


Before the real target: run the whole chain against a LOCAL copy of
the binary with the shipped libc — r2 -d lets you dmh-verify each
stage; only then fire remotely.

## The dry-run checks

- Each dmh state matches the plan.
- The leaks return the expected ranges.
- The aim lands (two-malloc verify).
- The write's read-back confirms.
- The firing condition is reachable.

## Falsifier

No local copy exists and the remote gives no heap view: build the
chain on observable behavior only — slower, but the same discipline.
