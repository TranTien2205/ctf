# Time budget

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

A sweep round costs ~10 agent-minutes; two failed
splits = re-classify, not a third fanout.

## Exit

Step done -> next phase module or merge rules.
