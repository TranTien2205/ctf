# exit — the clean ending


exit(0) — via exit@plt or syscall 60 — the clean termination after
the observable.

## The choice

- exit@plt: the libc path.
- syscall 60: the direct kernel path.
- main return: the loop.
