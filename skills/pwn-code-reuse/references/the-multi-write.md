# Multiple writes — the composite plant


Planting a multi-qword string or structure: several mov-store gadgets
in sequence, each writing 8 bytes — or a read() pulling the whole
block at once.

## The rule

Each write needs its own aim — the chain grows per qword; a bulk
read() is usually shorter.
