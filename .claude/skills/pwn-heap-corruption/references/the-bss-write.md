# The .bss write — the static target


A fixed .bss address (non-PIE) needs no leak: the slot array, the
count, a state flag — all at known addresses.

## Targets

- The slot array itself: write a pointer there → later ops use it.
- A count/limit global: expand the op budget.
- A state flag (is_admin): flip it — the gated path opens.

## Falsifier

PIE on with no base leak: .bss moves — need a code-pointer leak first.
