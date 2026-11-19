# Gadget quality — which gadgets are usable and which aren't

Not all gadgets are equal: a 'pop rdi; ret' is clean; 'pop rdi; pop rbp; ret' consumes an extra slot; a conditional gadget needs the right flags.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| pop rdi; ret | clean, one arg | use it |
| pop rdi; pop rbp; ret | consumes 2 slots | pad the extra |
| a gadget with side effects (call/add) | alters state | check the effect |
| an indirect gadget (jmp [reg]) | needs a register set | harder |

## Steps

1. pwn_triage --gadgets lists the matched gadgets.
2. A 'pop r; ret' consumes the next qword into r — fill it, then the next address.
3. A 'pop r; pop r2; ret' consumes TWO qwords — pad the second with junk or a value.
4. A gadget with a side-effect (a call, an add) changes state — account for it.

## Falsifier

Falsifier — the only available gadget for a needed register has a side-effect that breaks the chain: find a different chain shape.

## Traps

- Each gadget's side-effects must be neutral or useful — a stray 'call' can crash.
- The essential set: pop rdi, pop rsi, pop rdx, syscall, ret.
- A missing pop rdx is the classic hole — ret2csu or mov rdx gadgets cover it.

## Commands

```bash
python3 tools/pwn_triage.py ./chal --gadgets
r2 -A ./chal && /R pop
```

## Cross-references

`rop-basics.md` · `ret2csu.md`
