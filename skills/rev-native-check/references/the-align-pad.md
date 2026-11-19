# The padding — the struct's gaps


Struct padding bytes are indeterminate — a memcmp including padding
compares garbage bytes (usually still consistent).
