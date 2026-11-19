# Input via environment — env-var buffers

Environment variables land on the stack too: getenv() + strcpy into a buffer is a stack overflow via an env var.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| getenv('X') then strcpy | env input | X = payload |
| the env value reaches a stack buffer | env overflow | set it in the environment |

## Steps

1. Set the env var to the payload: X=$(python3 -c 'print(...)') ./chal.
2. The env string can contain any byte except \x00.
3. The overflow follows the same offset math as any input.

## Falsifier

Falsifier — the env var isn't copied to a stack buffer or is validated first: not this route.

## Traps

- env vars can't contain \x00 — same restriction as argv.
- env placement shifts stack addresses — a stack-target exploit needs the env accounted for.

## Commands

```bash
X=$(python3 -c 'print("A"*200)') ./chal
```

## Cross-references

`read-family.md`
