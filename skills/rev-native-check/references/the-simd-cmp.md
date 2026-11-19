# SIMD compares — the wide check


movdqu/pcmpeqb/pmovmskb compare 16 bytes at once — the operands are
the two 16-byte windows; the mask is the result.
