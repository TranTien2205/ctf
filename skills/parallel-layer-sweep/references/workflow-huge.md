# Variant: 10+ layer handouts

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

More layers than agents: batch by sink proximity,
sinks first - a dead sink eliminates its subtree.

## Exit

Step done -> next phase module or merge rules.
