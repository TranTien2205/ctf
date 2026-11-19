# The scanf family — a different boundary — checklist

Companion to `scanf-family.md`.

## Checklist

- [ ] Call | Real class
- [ ] scanf("%s",buf) | unbounded read → stack-smash
- [ ] scanf(buf,...) | buf is the format — unusual but possible
