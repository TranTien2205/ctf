# The two-part chain — when it can't fit


A chain longer than the buffer: split it — the overflow carries the
first part (pivot + the start), a planted region holds the rest.

## The delivery

    [pad][pivot → planted_region]
    planted_region: [the rest of the chain]
