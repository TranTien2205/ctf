# Fmtstr on a heap buffer — where the args point


If your input buffer is heap-allocated, it may not appear as a stack arg
at all — the pointer-plant must come from elsewhere.

## Steps

1. A heap buffer isn't a stack argument — %N$p won't see your bytes.
2. The primitive still reads/writes stack args — you just can't plant
   via input.
3. Plant the pointer via a first write, or use an existing arg.

## Falsifier

No plantable arg position exists: only reads of existing args.
