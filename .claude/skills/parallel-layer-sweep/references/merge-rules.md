# Merge order

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

Merge dead layers first (they bound the chain), then
reaches, then blocked. A reaches+dead conflict resolves
to the verbatim evidence, not the verdict.