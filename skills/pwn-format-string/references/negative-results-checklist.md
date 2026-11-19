# Negative results — recording dead routes — checklist

Companion to `negative-results.md`.

## Checklist

- [ ] Route | Negative | Reopens if
- [ ] the class | format arg literal | the input is the format
- [ ] arb-read | no plantable %N$s ptr | a position exists
- [ ] arb-write | no plantable %N$n ptr | a position exists
- [ ] GOT | full RELRO | partial
- [ ] ret-addr | stack addr unleakable | a leak
- [ ] hook | glibc ≥2.35 | ≤2.34
- [ ] blind | no oracle | a channel
