# Ranking the anomaly map

Method module for `white-box-intended-path`. Find the ONE
vulnerability the author wrote: diff against stock, map every
author-deliberate oddity, run the cheapest reachability
falsifier before committing to a chain.

Rank by (reachability, sink proximity, oddness) -
an unreachable oddity scores zero regardless of
how strange it is.

## Exit

Named next step -> that module.
