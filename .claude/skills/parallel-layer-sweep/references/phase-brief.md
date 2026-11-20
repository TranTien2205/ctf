# Phase: writing briefs

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

subagent_fanout.py --brief <handout> emits one brief per
layer: the layer's files, its falsifier, the layers a
kill map already closed. Hand the brief verbatim; do not
summarize it.