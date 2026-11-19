# Input via environment — env-var buffers — case catalogue

Environment variables land on the stack too: getenv() + strcpy into a buffer is a stack overflow via an env var.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | getenv('X') then strcpy | env input | X = payload |
| 2 | the env value reaches a stack buffer | env overflow | set it in the environment |

## Falsifier

Falsifier — the env var isn't copied to a stack buffer or is validated first: not this route.
