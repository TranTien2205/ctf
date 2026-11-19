# The argv/env layout — predicting stack contents — checklist

argv and env sit at the top of the stack: the first bytes a main() frame sees. Their layout predicts what the uninitialized-read leaks and where your shellcode/string can live.

## Checklist

- [ ] The stack top holds: argc, argv[0..n], NULL, envp[0..n], NULL, then auxv.
- [ ] Your env vars land there in order — a controlled env string is at a predictable-ish address (modulo argv/env lengths).
- [ ] An uninit read leaking these pointers gives stack addresses without ASLR help.
- [ ] A /bin/sh string planted in env has a stack address you can compute.

## Abort conditions

- Env-var strings are \x00-free but otherwise arbitrary bytes.
- The exact stack address depends on argv+env byte count — it shifts with the environment.

## Falsifier

Falsifier — the environment layout differs from the assumed model (different argv, stripped env): the predicted address is wrong; re-derive it.
