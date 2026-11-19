# test vs cmp — the two compares


- cmp a, b: a - b, sets flags — the difference check.
- test a, a: a & a — the zero/nonzero check — tests a call's return
  (strcmp's 0 = equal).

## The pair

`call strcmp; test eax, eax; jz` = "if equal" — the standard shape.
