# The dependency chain — what precedes what


The order of dependencies: IP control → (canary leak) → (stack leak
for ret writes) → gadget addresses (base leak for PIE) → the chain →
the call → the flag.

Each arrow is a prerequisite — a missing one stops the chain.
