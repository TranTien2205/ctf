# Leaking libc — the GOT-read path


A libc pointer comes from a GOT entry: plant the GOT slot's address and
%s it — the resolved import's libc address leaks.

## Steps

1. Non-PIE: the GOT slot address is fixed — plant it.
2. %N$s on the planted GOT-addr: prints the resolved libc function's
   bytes as a string — first 6-8 bytes are the address (little-endian).
3. libc_base = leaked - symbol_offset (know the libc version).

## Reading the leak

The %s output is raw bytes until a NUL — the address is the first 6-8
bytes, often needing unhex/unpack.

## Falsifier

Full RELRO: GOT holds real addresses anyway (it does) — the leak still
works; RELRO blocks only the GOT *write*. The falsifier is: no
plantable arg or no imported function with a known libc offset.
