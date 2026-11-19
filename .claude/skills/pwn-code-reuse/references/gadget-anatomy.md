# Gadget anatomy — the ret-terminated tail


A gadget is a byte sequence inside the binary ending in ret (0xc3):
`pop rdi ; ret` sets rdi and returns to the next chain entry — the
chain is stack data the ret's consume.

## The shape

    [addr of pop rdi; ret] [the rdi value] [next gadget] ...

Each ret pops the next address — the stack pointer walks the chain.

## Finding them

- python3 tools/pwn_triage.py ./chal --gadgets — the essential set.
- r2 -A ./chal then /R <pattern> — the full search.

## Falsifier

No usable gadget sequence exists (tiny static binary): the chain can't
express the needed action — see the minimal-gadget recipes.
