# Input via environment — env-var buffers — checklist

Environment variables land on the stack too: getenv() + strcpy into a buffer is a stack overflow via an env var.

## Checklist

- [ ] Set the env var to the payload: X=$(python3 -c 'print(...)') ./chal.
- [ ] The env string can contain any byte except \x00.
- [ ] The overflow follows the same offset math as any input.

## Abort conditions

- env vars can't contain \x00 — same restriction as argv.
- env placement shifts stack addresses — a stack-target exploit needs the env accounted for.

## Falsifier

Falsifier — the env var isn't copied to a stack buffer or is validated first: not this route.
