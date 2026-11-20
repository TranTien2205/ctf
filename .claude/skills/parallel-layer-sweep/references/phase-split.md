# Phase: splitting layers

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

novel_plan.py --source <handout> names mechanism layers,
each with its own falsifier. A layer is one mechanism
boundary (parser, auth check, query builder, sink) - not
one file.