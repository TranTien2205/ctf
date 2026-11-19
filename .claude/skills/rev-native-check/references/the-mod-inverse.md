# The modular inverse — dividing mod 2^n


For odd k: input = expected * k^(-1) mod 2^32 — Python:

    inv = pow(k, -1, 1<<32)
    answer = (expected * inv) % (1<<32)

The even-k case loses bits — brute the lost bits.
