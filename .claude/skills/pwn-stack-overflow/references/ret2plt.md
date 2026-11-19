# ret2plt / ret2system — call an imported function

system@plt, puts@plt, printf@plt: imported functions have static PLT stubs even under PIE. If the binary imports system and you control a string argument, ret2plt is the shortest chain.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| system in the import table | ret2system exists | one call |
| a '/bin/sh' string in .rodata or writable | arg available | rdi=string, call system |
| non-PIE or partial-RELRO | PLT address stable | direct call |

## Steps

1. Check imports: readelf -s ./chal | grep FUNC or r2 -A && afl — look for system/execve/popen.
2. Find a '/bin/sh' or '/bin/cat flag' string: r2 -A && izz | grep -i sh or strings -tx ./chal | grep -iE 'sh$|flag'.
3. Need pop rdi; ret gadget for the arg — tools/pwn_triage.py --gadgets lists it.
4. Chain: pad + pop rdi;ret + binsh_addr + system@plt.

## Falsifier

Falsifier — no exec-like import and no useful PLT target: ret2plt is out; ret2libc or code-reuse chains remain.

## Traps

- system@plt needs /bin/sh reachable — find or write it.
- rdi is the first arg on x64 — pop rdi;ret is the gadget; tools/pwn_triage.py lists it.
- Some PLT stubs need a second ret for stack alignment before libc calls.

## Commands

```bash
readelf -s ./chal | grep FUNC
r2 -A ./chal && izz | grep -i sh
python3 tools/pwn_triage.py ./chal --gadgets
```

## Cross-references

`ret2win.md` · `ret2libc.md` · `rop-basics.md`
