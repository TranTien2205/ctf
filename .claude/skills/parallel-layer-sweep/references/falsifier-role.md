# Why every layer has a falsifier

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

novel_plan's per-layer falsifier is the cheap test that
proves the layer dead - the agent runs it FIRST, so a
dead layer costs one probe, not a reading session.