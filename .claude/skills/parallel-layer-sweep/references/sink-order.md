# Sink-first ordering

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

When layers outnumber agents, brief the sinks first:
a proven-dead sink prunes every layer feeding it.