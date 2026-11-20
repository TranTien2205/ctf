# Phase: the stock diff

Method module for `white-box-intended-path`. Find the ONE
vulnerability the author wrote: diff against stock, map every
author-deliberate oddity, run the cheapest reachability
falsifier before committing to a chain.

Fetch the upstream version the handout is based on
(package.json/go.mod/pom versions name it); diff
the handout against it - every delta is author-
deliberate by construction.

## Exit

Named next step -> that module.
