# Falsifiers — what closes each route

| Route | Falsifier |
|---|---|
| the class | format arg is a literal |
| %p leak | output truncated; args unreachable |
| %s arb-read | no pointer at a %N$s position |
| %n arb-write | no pointer at a %N$n position |
| GOT overwrite | full RELRO |
| ret-addr | stack addr unleakable |
| __free_hook | glibc ≥ 2.35 |
| offset find | input never a %N$p value |
| blind fmtstr | no output channel |
| byte-write | count can't reach the value |

Class falsifier: printf("%s", user_input) — the input is an argument to a
literal format, so nothing is interpreted. Full RELRO additionally closes
the GOT route whatever the leak is worth.
