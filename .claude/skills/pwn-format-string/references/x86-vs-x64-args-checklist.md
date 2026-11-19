# x86 vs x64 argument layout — where your buffer sits — checklist

x86 puts all args on the stack (low N reaches your input); x64 puts the first 6 in registers (your input is at high N). The arg-offset differs fundamentally.

## Checklist

- [ ] Check ELF class: readelf -h | grep Class.
- [ ] x86: input often at N=1-8; the args are all stack words.
- [ ] x64: input usually at N=6-20; registers hold the first 6.
- [ ] Measure N empirically with AAAA.%N$p — don't assume.

## Abort conditions

- x86 %1$p is your data quickly; x64 needs higher N.
- The register args on x64 mean the FIRST %p values aren't stack memory.

## Falsifier

Falsifier — the ABI/layout assumption doesn't match the measured N: always measure; the N is per-call-site.
