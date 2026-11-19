# Ending in a loop — the persistent exploit


A chain ending back at the read loop keeps the service alive — useful
for multi-stage attacks and attack-defense persistence.

## The shape

    ...chain... [ret to main/loop]

## Falsifier

The loop path corrupts state (a reset wipes the planted data): end
cleanly instead.
