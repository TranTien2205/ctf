# Input via argv — when the read is the command line — case catalogue

Some binaries take input as argv[1] instead of stdin: the overflow is in an argument. The payload goes in the argument position.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | main uses argv[1] directly | argv input | the arg is the buffer |
| 2 | copied into a stack buffer | argv overflow | argv[1] = payload |

## Falsifier

Falsifier — the input isn't argv — check stdin/protocol paths.
