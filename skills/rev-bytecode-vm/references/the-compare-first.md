# Compare-first — the direct equality VM

The simplest flag-checker: compare input to a stored array — the
expected bytes ARE the flag.

    0x10        ; read flag[i]
    0x01 0x66   ; push 'f'
    0x20        ; cmp_eq
    0x30 +4     ; jz continue

The pushed constants are the flag bytes — extract them in order.
