# The setbuf trick — planting a controlled frame


setbuf(stream, buf) sets a stream's buffer to a caller-supplied address
— paired with a write to that buffer, it plants controlled data where
the stream machinery later uses it.

## The niche

Rare — a specialized primitive when the normal plant path is closed.
