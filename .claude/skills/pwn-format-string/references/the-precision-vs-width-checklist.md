# Precision vs width — the two count controls — checklist

Companion to `the-precision-vs-width.md`.

## Checklist

- [ ] Specifier | Effect
- [ ] %999c | width = 999 bytes
- [ ] %999d | precision/width = 999
- [ ] %.999s | precision caps output
- [ ] 1. %Nc prints N chars — the count rises by N.
- [ ] 2. %Nd with a field width of N prints N chars — same effect.
- [ ] 3. %.Ns PRECISION caps a string's printed length — a limit.
