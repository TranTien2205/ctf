# The input op — which instruction reads the flag

The flag-checking VM reads the flag one op at a time. Find the op
that consumes input bytes.

## The recognisable handler

    case 0x10: stack[sp++] = flag[fp++];  // read next flag byte

or

    case 0x10: push(argv[1][ip++]);        // the argv flag

The `input`/`flag`/`argv[1]` read inside a handler IS the input op —
the program pulls bytes from the supplied string.

## Decoding around it

Each `read_char` in the program stream is one flag byte consumed —
the count of read ops = the flag length.

## The transform ops

After a read, transform ops (add/xor/rol) mutate the byte before
the cmp — read the program's op sequence to reconstruct it.

## The cmp op

    case 0x20: a=pop(); b=pop(); push(a==b);

The compare pops the transformed input and the expected — the
expected is the constant pushed before it.
