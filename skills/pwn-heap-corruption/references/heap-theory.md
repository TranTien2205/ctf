# Why heap corruption works — the theory


glibc's allocator keeps its bookkeeping inline with user data: chunk
headers precede buffers, free-chunk links live inside freed buffers.
The allocator trusts these fields — corrupting them makes the
allocator itself the confused deputy: it writes where its links point.

## The three trust violations

- Size fields: believed → boundary confusion.
- fd/bk links: followed → the bin write.
- counts/keys: checked → the detection walls.

Every technique corrupts one of the three; every mitigation verifies
one.
