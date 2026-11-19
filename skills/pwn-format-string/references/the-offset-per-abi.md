# Offset per ABI — SysV vs Windows vs x86


Argument indexing is ABI-specific: SysV x64 (6 reg varargs), Windows x64
(4), x86 cdecl (0 — all on stack). The arg-offset N differs.

| ABI | Register varargs | Stack args start |
|---|---|---|
| SysV x64 | %1-%6 | %7+ |
| Windows x64 | %1-%4 | %5+ |
| x86 cdecl | none | %1+ |

## Falsifier

ABI misidentified: measure N empirically; the sweep is ABI-agnostic.
