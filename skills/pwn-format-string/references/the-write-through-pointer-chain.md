# The write-through-pointer-chain — *ptr where ptr is controlled


%n writes to *arg — if you control arg, you control WHERE it writes. The
pointer is a value in your input, the count is the value written.

## The mechanics

- arg = a pointer you set → *arg = the target.
- The pointer inside your input → the arg is yours.
- The count via %c → the value written.

## Steps

1. Plant the target's address as an argument (in your input).
2. %n writes the cumulative count to *that-address.
3. The pointer is the destination; the count is the value.
4. The address must be at a %N$n-readable position.

## Falsifier

The pointer can't be placed at a %N$n position: no controlled write
destination.
