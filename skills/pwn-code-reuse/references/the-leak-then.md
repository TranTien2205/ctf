# Leak then chain — the dependency


The chain can't be finalized until the leak arrives — the order is:

1. Leak fires (stage 1).
2. The base is computed.
3. The chain is assembled with real addresses.
4. The chain fires (stage 2).

On a one-shot service, stages 1 and 2 merge — a harder problem.
