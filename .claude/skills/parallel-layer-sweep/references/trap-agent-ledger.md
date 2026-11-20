# Trap: agents writing state

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

An agent posting to state.json races the controller -
the merge step exists so the main thread owns every
write.