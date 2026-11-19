# Multiple chains — the compound exploit


An exploit may need several chains in sequence: leak + plant + call —
each a separate overflow or stage.

## The orchestration

Each stage's output feeds the next — the state between them (the
leaked base, the planted data) is the exploit's memory.
