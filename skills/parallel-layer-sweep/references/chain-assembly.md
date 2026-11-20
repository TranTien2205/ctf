# Assembling the chain

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

Merge produces a layer sequence entry->sink; the
chain is viable only if every hop is 'reaches'.
One 'blocked' hop needs its bypass, not a retry.

## Exit

Step done -> next phase module or merge rules.
