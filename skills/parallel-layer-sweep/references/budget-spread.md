# Budget across layers

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

The challenge budget divides across layers, not agents:
a layer's five-probe bound is spent by whichever agent
probes it.