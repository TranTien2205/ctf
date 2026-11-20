# Phase: merging

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

--merge prints the hooks.py commands for the MAIN
thread. The main thread runs them; agents never
post-probe themselves.