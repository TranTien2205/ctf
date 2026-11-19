# rdx substitutes — when pop rdx is missing


`pop rdx; ret` is the scarcest common gadget — substitutes:

- `mov rdx, rXx; ret` where rXX you control.
- `xor edx, edx; ret` for NULL.
- ret2csu's mov rdx, r15 sequence.
- A `pop rXX`-that-aliases-rdx on some encodings.

## Falsifier

No path reaches rdx: three-arg calls are out — design for <= 2 args.
