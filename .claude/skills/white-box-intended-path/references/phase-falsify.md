# Phase: cheapest falsifier

Method module for `white-box-intended-path`. Find the ONE
vulnerability the author wrote: diff against stock, map every
author-deliberate oddity, run the cheapest reachability
falsifier before committing to a chain.

Before committing to a chain: run the cheapest
reachability falsifier on its first hop. A dead
first hop kills the chain for one probe.

## Exit

Named next step -> that module.
