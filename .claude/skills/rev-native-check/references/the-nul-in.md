# The NUL in input — the terminated compare


The compare may expect a NUL-terminated string — the produced input's
terminator placement matters for strcmp but not memcmp.
