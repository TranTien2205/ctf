# Class boundary — what format-string is NOT

| Shape | Real class |
|---|---|
| a bounded strcpy into a stack buffer | `pwn-stack-overflow` |
| printf("%s", buf) — input is an arg | not a format bug |
| an unbounded copy, not a format | `pwn-stack-overflow` |
| heap metadata corruption | `pwn-heap-corruption` |

## The deciding question

Is your input the FORMAT argument to a printf-family call? Yes → here.
An argument TO a literal format → closed. An unbounded copy → stack-smash.
