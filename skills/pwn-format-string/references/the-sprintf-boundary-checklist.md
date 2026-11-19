# The sprintf boundary — the hidden overflow + fmtstr — checklist

Companion to `the-sprintf-boundary.md`.

## Checklist

- [ ] sprintf writes the formatted output to dst.
- [ ] A large %Nc output overflows a stack dst.
- [ ] The format string is your input (the fmtstr), and its OUTPUT is the
- [ ] 1. Check dst's allocation — is it a stack buffer?
- [ ] 2. If yes, a large %Nc output overflows it.
- [ ] 3. The specifiers' effect AND the output's overflow compose.
