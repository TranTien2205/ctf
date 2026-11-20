# tools/forensics/*

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

artifact_inventory.py, evtx/hive/mft/prefetch/
lnk/amsi/squashfs/dtb readers - the stdlib
forensics stack for structured artifacts.

## Pivot

Artifact identified -> its route-* module and depth skill.
