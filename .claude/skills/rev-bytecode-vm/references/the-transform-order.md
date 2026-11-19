# The transform order — read the ops carefully

The transform's op order matters: `read; xor k; add m; cmp` is
`((flag ^ k) + m) == exp` — invert in reverse: `flag = (exp - m) ^ k`.

## The rule

Read the op sequence in EXECUTION order, write the inversion in
reverse order — each op's inverse applied last-to-first.
