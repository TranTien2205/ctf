# The recv shape — reading the response


The response's shape decides the parse:

- Fixed-size: recv(n) until n bytes.
- Delimited: until a marker (a newline, a prompt).
- Timed: until quiet — a heuristic, not a guarantee.

## The rule

Match the parse to what the protocol actually sends — the leak's
bytes have a known shape.
