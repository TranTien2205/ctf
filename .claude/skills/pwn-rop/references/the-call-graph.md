# The call graph — re-entry feasibility


The re-entry target must be reachable — the call graph from the
re-entry point back to the read: main→vuln reads again; a dead-end
function doesn't.
