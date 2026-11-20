# eval vs exec — the two sinks

`eval(expr)` returns a value; `exec(code)` runs statements — a jail
may expose one and not the other; exec reaches assignments and
imports that eval cannot.

## The difference

eval returns; exec assigns + imports — the exposed one shapes the escape.
