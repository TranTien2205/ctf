# Family: fetch

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

The `fetch` family runs as `ctf-web-fetch` and owns: ssrf, open-redirect, request-smuggling.

## What it returns

The contract JSON - disposition (closed/open/not-measured/parked),
evidence as a verbatim response excerpt, falsifier_state, and the
next_probe the family suggests. Its brief carries the classes'
first_probe and falsifier fields read from the taxonomy.

## Independence

This family shares no state with the others - its measurements are
bounded by its own brief's scope and never touch the ledger.
