# The constant offsets — known-good values


The chain's offsets (gadget offsets, symbol offsets) come from the
shipped binary/libc — compute them once per build:

    r2 -A ./chal ; /R pop rdi    → the offset
    readelf -s libc.so.6 | grep ' system'   → the symbol
