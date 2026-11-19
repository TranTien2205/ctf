# Tracing — the (pc, op, stack) log

When static decode fails, log the execution:

    while pc < n:
        log(pc, prog[pc], stack)
        execute(prog[pc])

## The trace's use

- The executed op sequence IS the program's behavior.
- The stack contents per op show the transform's intermediate
  values.
- The cmp operands reveal the expected byte.
