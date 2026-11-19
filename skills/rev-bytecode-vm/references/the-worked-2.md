# Worked — the custom VM


1. The loop: pc++, dispatch[op] — 16 opcodes.
2. Handlers recovered: push,pop,add,xor,cmp,jz,call,ret,print,halt.
3. The program's byte-stream decodes: transform + compare to const.
4. Invert the transform → accepted input.
