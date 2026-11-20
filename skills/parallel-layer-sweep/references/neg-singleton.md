# Negative: single-mechanism handout

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

novel_plan returns one layer - sequential probing is
cheaper; do not force a split.