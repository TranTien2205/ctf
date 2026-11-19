# The clean exit — ending the chain


A chain that ends abruptly crashes — often fine, but a clean exit
(exit(0)) or a ret into a loop preserves service for the next
connection.

## The ending choices

- A ret to exit() — clean termination.
- A ret to main/the read loop — persistent exploitation.
- A crash — acceptable if the flag already printed.

## Falsifier

None — cosmetic, not correctness.
