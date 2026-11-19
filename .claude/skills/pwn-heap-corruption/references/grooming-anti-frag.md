# Making grooming robust — determinism tricks


The heap's initial state varies run to run — robust exploits normalize
it before corrupting.

## The normalization

- Spray a known number of filler allocs to reach a deterministic bin
  state.
- Free in a fixed pattern; allocate guards to fence the layout.
- Use a fresh connection where the heap is predictable (early
  allocations have a known layout).
- Consume the "unknown" frees first so later state is deterministic.

## Verify

dmh the heap after normalization — the layout should match the plan
exactly before the corruption op runs.

## Falsifier

The service's heap is shared/async — normalization can't hold: pick a
primitive robust to interleaving.
