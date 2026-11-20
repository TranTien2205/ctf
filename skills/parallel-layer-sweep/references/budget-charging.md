# Charging the budget

Method module for `parallel-layer-sweep`. Close a layered
white-box handout in parallel: novel_plan splits layers, one
ctf-layer-prober per layer, validate, merge through the
main thread. Agents measure; they never write state.

Each probe an agent ran is charged to that layer's
five-probe bound via the merge's state write - the
main thread does the charging.

## Exit

Step done -> next phase module or merge rules.
