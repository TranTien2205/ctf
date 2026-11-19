# Worked — a .NET flag-checker — checklist

Companion to `the-worked-dotnet.md`.

## Checklist

- [ ] 1. rabin2 -I: CLR directory non-zero → managed.
- [ ] 2. dotnet_info --strings: 'Enter flag' + a 40-char literal.
- [ ] 3. The CheckFlag MethodDef's IL: xor each byte with 0x5a, compare
- [ ] 4. Invert: flag = xor(literal, 0x5a).
- [ ] 5. Run → accepted.
