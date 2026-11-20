# Partial merges

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

Some agents failing or timing out: merge what
validated, re-brief only the missing layers - the
sweep is checkpointed by contract.