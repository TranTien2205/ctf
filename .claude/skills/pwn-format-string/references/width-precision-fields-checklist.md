# Width and precision fields — controlling the count — checklist

Companion to `width-precision-fields.md`.

## Checklist

- [ ] Specifier | Effect
- [ ] %Nc | N bytes printed
- [ ] %999d with width 999 | 999 chars
- [ ] the running total | all printed bytes = the %n value
- [ ] 1. %Nc prints N chars — the count rises by N.
- [ ] 2. %Nd with a width of N prints N chars — same effect.
- [ ] 3. The %n after it writes the cumulative count.
- [ ] 4. Plan the count: which value do you need written?
