# eval() vs parse+dispatch — the safety split

`eval(expr)` on a puzzle expression is fast to write but brittle:
`*`, `//`, precedence quirks, injected chars. `ast.literal_eval` or a
hand parser keeps the grammar you actually accept.

## The discipline

Parse the grammar you accept — never eval bytes you didn't shape.

## Accepted grammar

literal_eval or a hand parser — never raw eval.
