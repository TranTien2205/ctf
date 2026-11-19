# The real-link chain — legitimate bin state


Before corrupting: know what the bin LOOKS like clean — head, the fd
chain, the tail's null — so the forge mirrors a plausible bin.

## Steps

1. dmh the bins in a clean run — record head/count/links.
2. Forge the corruption to produce a plausible post-state.
3. A bin that can't exist (cycle, wrong count, bad alignment) is
   detectable in review.

## Falsifier

None — observation discipline.
