# The argv/env layout — predicting stack contents

argv and env sit at the top of the stack: the first bytes a main() frame sees. Their layout predicts what the uninitialized-read leaks and where your shellcode/string can live.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| an env var holds your string | env region address needed | predictable offset |
| uninit read leaks argv/env pointers | stack-pointer leak | the layout |
| a string must live at a known address | env or argv region | the layout |

## Steps

1. The stack top holds: argc, argv[0..n], NULL, envp[0..n], NULL, then auxv.
2. Your env vars land there in order — a controlled env string is at a predictable-ish address (modulo argv/env lengths).
3. An uninit read leaking these pointers gives stack addresses without ASLR help.
4. A /bin/sh string planted in env has a stack address you can compute.

## Falsifier

Falsifier — the environment layout differs from the assumed model (different argv, stripped env): the predicted address is wrong; re-derive it.

## Traps

- Env-var strings are \x00-free but otherwise arbitrary bytes.
- The exact stack address depends on argv+env byte count — it shifts with the environment.

## Commands

```bash
./chal   # main's stack starts below argv/env
```

## Cross-references

`env-control.md` · `argv-control.md`
