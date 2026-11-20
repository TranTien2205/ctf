# Layer type: input validation

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

Type/length/format checks - falsifier is a value
violating the stated rule reaching the next layer.
Weak validators pass type-coerced input.

## Exit

Step done -> next phase module or merge rules.
