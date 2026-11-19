# The deciding check — what it is


The deciding check is the one comparison the flag actually passes
through — the cmp/test/call whose result picks the yes-branch. The
work is finding IT, not describing the binary.

## The three shapes

- A constant vs the input — read the constant.
- A transform vs a stored constant — invert the transform.
- A digest vs a stored digest — can't invert; patch or find the
  digest's source.
