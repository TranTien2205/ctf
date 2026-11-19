# Recovering the dispatch table — the ISA — checklist

Companion to `dispatch-table-recovery.md`.

## Checklist

- [ ] Which op reads the input? (load_input / read_char)
- [ ] Which op compares? (cmp, test, jz)
- [ ] Which op wins? (print win / return true)
