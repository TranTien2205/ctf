# sendall — the write half

`s.sendall(b)` loops until the bytes are out — a plain `send` can
short-write; for one-line answers it rarely bites, for grids it
does.
