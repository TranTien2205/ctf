# tools/sc_gen.py — tested shellcode stubs — case catalogue

Emits tested shellcode stubs: execve64/execve86 (shell), cat64 (read /flag), rev64 (reverse shell). --raw for hex-only output; it reports any banned bytes present.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | execve64/execve86 | system shell | the exec stubs |
| 2 | cat64 | cat a file (--path) | read flag |
| 3 | rev64 | reverse shell (--host/--port) | network shell |
| 4 | --raw | hex only | pipe into payloads |

## Falsifier

Falsifier — NX is on: no shellcode executes; the stub is useless, go to ROP.
