# The measurement contract

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

--contract is the single source of truth for what a
subagent returns: layer id, verdict (reaches/blocked/
dead), verbatim evidence, falsifier status, next
candidate layer.