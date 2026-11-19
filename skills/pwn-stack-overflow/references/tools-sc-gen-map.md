# tools/sc_gen.py — tested shellcode stubs — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| execve64/execve86 | system shell | the exec stubs |
| cat64 | cat a file (--path) | read flag |
| rev64 | reverse shell (--host/--port) | network shell |
| --raw | hex only | pipe into payloads |

## Falsifier

Falsifier — NX is on: no shellcode executes; the stub is useless, go to ROP.
