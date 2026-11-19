# ECMA-335 — the .NET metadata layout — checklist

Companion to `the-ecma335.md`.

## Checklist

- [ ] `#~` — the tables stream: TypeDef, MethodDef, MemberRef, ...
- [ ] `#Strings` — identifier names.
- [ ] `#US` — the user-string heap: every `ldstr` literal — flag-check
- [ ] `#Blob` — signatures and misc.
