# The hash shape — the digest compare


The input is hashed and the digest compared — can't invert a digest:
the options are patch the jump, or find the digest-computation input
(the pre-image may be derivable another way).

## The check

Is it really a one-way digest, or a weak checksum (crc32, a sum)?
A weak checksum inverts or collides.
