# Coverage metric

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

Layers measured / layers planned - below 100% the
sweep is incomplete, not failed; unmeasured layers
are named in the report.

## Exit

Step done -> next phase module or merge rules.
