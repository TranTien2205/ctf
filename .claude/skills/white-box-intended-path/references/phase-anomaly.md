# Phase: the anomaly map

Method module for `white-box-intended-path`. Find the ONE
vulnerability the author wrote: diff against stock, map every
author-deliberate oddity, run the cheapest reachability
falsifier before committing to a chain.

Every delta lands in the anomaly map: file, shape
(added endpoint, weakened check, odd constant,
vendored change), and a reachability guess. The
map is the method's product.

## Exit

Named next step -> that module.
