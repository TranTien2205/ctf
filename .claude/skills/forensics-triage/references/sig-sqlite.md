# Signature: SQLite

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

'SQLite format 3\x00' - browser artifacts, app
databases; sqlite3 CLI or python sqlite3.

## Pivot

Artifact identified -> its route-* module and depth skill.
