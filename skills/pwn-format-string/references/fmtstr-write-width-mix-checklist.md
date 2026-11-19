# Mixed write widths — combining %hhn + %hn + %n — checklist

Companion to `fmtstr-write-width-mix.md`.

## Checklist

- [ ] 1. Each %N$hhn/%hn/%n consumes its arg position and writes count&width.
- [ ] 2. Mix widths per target; order by the count each needs.
- [ ] 3. The count is shared — plan the cumulative sequence.
