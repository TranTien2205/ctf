# ret2plt / ret2system — call an imported function — checklist

system@plt, puts@plt, printf@plt: imported functions have static PLT stubs even under PIE. If the binary imports system and you control a string argument, ret2plt is the shortest chain.

## Checklist

- [ ] Check imports: readelf -s ./chal | grep FUNC or r2 -A && afl — look for system/execve/popen.
- [ ] Find a '/bin/sh' or '/bin/cat flag' string: r2 -A && izz | grep -i sh or strings -tx ./chal | grep -iE 'sh$|flag'.
- [ ] Need pop rdi; ret gadget for the arg — tools/pwn_triage.py --gadgets lists it.
- [ ] Chain: pad + pop rdi;ret + binsh_addr + system@plt.

## Abort conditions

- system@plt needs /bin/sh reachable — find or write it.
- rdi is the first arg on x64 — pop rdi;ret is the gadget; tools/pwn_triage.py lists it.
- Some PLT stubs need a second ret for stack alignment before libc calls.

## Falsifier

Falsifier — no exec-like import and no useful PLT target: ret2plt is out; ret2libc or code-reuse chains remain.
