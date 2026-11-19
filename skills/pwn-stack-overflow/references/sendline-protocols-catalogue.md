# The sendline protocol — remote service shape — case catalogue

A remote pwn service reads a line, processes it, responds. The payload must survive the transport: newlines, length limits, and the service's framing.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | nc gives a prompt then reads | line-oriented | send + newline |
| 2 | binary protocol with a length field | framed | length prefix matters |
| 3 | the service echoes the input | echo oracle | verify bytes landed |

## Falsifier

Falsifier — the service's read bound stops before your offset: the payload can't reach the saved state at this size.
