# Offset per ABI — SysV vs Windows vs x86 — map

Companion to `the-offset-per-abi.md`.

| ABI | Register varargs | Stack args start |
|---|---|---|
| SysV x64 | %1-%6 | %7+ |
| Windows x64 | %1-%4 | %5+ |
| x86 cdecl | none | %1+ |
## Falsifier
