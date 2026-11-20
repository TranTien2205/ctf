# Phase: spawning

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

One ctf-layer-prober per brief, all parallel. Each agent
reads code and returns a measurement contract - none
touches state.json or the ledger.