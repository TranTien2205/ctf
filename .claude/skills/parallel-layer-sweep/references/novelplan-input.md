# novel_plan as input

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

The sweep is only as good as the split - a wrong
layer boundary shows as agents reporting the same
mechanism from different briefs.

## Exit

Step done -> next phase module or merge rules.
