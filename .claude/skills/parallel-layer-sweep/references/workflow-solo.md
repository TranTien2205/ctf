# Variant: solo-layer challenges

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

novel_plan returning 1-2 layers - sweep degenerates
to sequential probing; keep the falsifier discipline
anyway.

## Exit

Step done -> next phase module or merge rules.
