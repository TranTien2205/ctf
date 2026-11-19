# The practice loop — the dry-run


Locally, under r2 -d:

- dmh after every op — watch the bins respond.
- Verify the leak lands on an arena pointer.
- Verify the aim's two-alloc lands the target.
- Verify the write's read-back.

Then remotely — same sequence, the same checkpoints by behavior (the
service's responses, not dmh).
