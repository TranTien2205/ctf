# The pointer inside your input — where the arg lives


The pointer %s derefs / %n writes-to lives inside YOUR input bytes —
you place an 8-byte address at the offset where the printf arg reads it.

## How

- Your input is read as bytes — an 8-byte little-endian address at the
  right offset becomes arg N's pointer.
- Place the target address at the byte-offset inside the input where
  arg[N] reads it.
- The arg-offset-finder locates which N reads which input bytes.
- Pack the address with struct.pack('<Q', addr).

## Falsifier

The input bytes can't reach a %N$s/%N$n position as a pointer: no
deref/write.
