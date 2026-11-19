# x86 vs x64 argument layout — where your buffer sits

x86 puts all args on the stack (low N reaches your input); x64 puts the first 6 in registers (your input is at high N). The arg-offset differs fundamentally.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| ELF32 | all args on stack | low N |
| ELF64 | 6 in regs, then stack | high N |
| the buffer's N differs | the ABI decides | measure it |

## Steps

1. Check ELF class: readelf -h | grep Class.
2. x86: input often at N=1-8; the args are all stack words.
3. x64: input usually at N=6-20; registers hold the first 6.
4. Measure N empirically with AAAA.%N$p — don't assume.

## Falsifier

Falsifier — the ABI/layout assumption doesn't match the measured N: always measure; the N is per-call-site.

## Traps

- x86 %1$p is your data quickly; x64 needs higher N.
- The register args on x64 mean the FIRST %p values aren't stack memory.

## Commands

```bash
readelf -h ./chal | grep Class
```

## Cross-references

`arg-offset-finder.md` · `the-stack-args.md`
