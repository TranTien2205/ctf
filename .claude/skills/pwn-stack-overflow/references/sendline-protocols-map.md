# The sendline protocol — remote service shape — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| nc gives a prompt then reads | line-oriented | send + newline |
| binary protocol with a length field | framed | length prefix matters |
| the service echoes the input | echo oracle | verify bytes landed |

## Falsifier

Falsifier — the service's read bound stops before your offset: the payload can't reach the saved state at this size.
