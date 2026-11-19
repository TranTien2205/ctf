# Falsifiers — what closes each route — checklist

Companion to `falsifiers.md`.

## Checklist

- [ ] Route | Falsifier
- [ ] the class | format arg is a literal
- [ ] %p leak | output truncated; args unreachable
- [ ] %s arb-read | no pointer at a %N$s position
- [ ] %n arb-write | no pointer at a %N$n position
- [ ] GOT overwrite | full RELRO
- [ ] ret-addr | stack addr unleakable
- [ ] __free_hook | glibc ≥ 2.35
- [ ] offset find | input never a %N$p value
- [ ] blind fmtstr | no output channel
- [ ] byte-write | count can't reach the value
