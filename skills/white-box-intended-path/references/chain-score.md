# Scoring candidate chains

Method module for `white-box-intended-path`. Find the ONE
vulnerability the author wrote: diff against stock, map every
author-deliberate oddity, run the cheapest reachability
falsifier before committing to a chain.

Chains score on measured hops, untested-hop count,
and falsifier cost - the cheapest-untested chain
probes first.

## Exit

Named next step -> that module.
