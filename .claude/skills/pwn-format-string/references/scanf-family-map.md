# The scanf family — a different boundary — map

Companion to `scanf-family.md`.

| Call | Real class |
|---|---|
| scanf("%s",buf) | unbounded read → stack-smash |
| scanf(buf,...) | buf is the format — unusual but possible |
## The distinction
## Falsifier
