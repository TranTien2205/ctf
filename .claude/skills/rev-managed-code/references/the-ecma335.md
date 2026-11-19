# ECMA-335 — the .NET metadata layout

.NET metadata lives in streams inside the PE:

- `#~` — the tables stream: TypeDef, MethodDef, MemberRef, ...
- `#Strings` — identifier names.
- `#US` — the user-string heap: every `ldstr` literal — flag-check
  strings live here.
- `#Blob` — signatures and misc.

## The local tool

    python3 tools/dotnet_info.py app.exe
    python3 tools/dotnet_info.py app.exe --strings   # #US heap

dotnet_info walks #~: TypeDefs (namespace+name), MethodDefs with
RVAs, MemberRefs — the metadata map without a decompiler.
