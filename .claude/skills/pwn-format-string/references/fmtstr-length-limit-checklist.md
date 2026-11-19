# Format-string length limits — fitting the payload — checklist

Companion to `fmtstr-length-limit.md`.

## Checklist

- [ ] %N$hhn is shorter than %N$n equivalent.
- [ ] Positional args skip the consuming specifiers.
- [ ] The pointer can ride inside the same input — one field holds both
