# The fork-stage — keeping the service


A chain ending in a return to the read loop (not exit) keeps the
service alive — useful for multi-run exploits and attack-defense.

## The shape

    ... chain ... [main_addr or the loop entry]

## The rule

The loop's state must survive — a reset wiping your planted data
kills the staged approach.
