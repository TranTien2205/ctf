# Math rounds — parse leniently

`round N: a+b=?` — regex the operands and the operator, never fixed
offsets: late rounds add operators, widen numbers, change spacing.
`eval` is tempting but brittle — parse + dispatch.

## Dispatch

A dict of operators — new ops are entries, not rewrites.

## Dispatch

A dict of operators — new ops are entries, not rewrites.
