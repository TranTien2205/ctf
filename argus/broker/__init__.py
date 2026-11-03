"""The tool plane.

Every command that touches a target goes through this package, and every call
passes the ledger gate on the way in and the way out. That single choke point is
what makes the layer above it — a model deciding what to run — safe to automate:

    model -> MCP tools/call -> pre_probe (scope, tier, class, budget)
                            -> argv exec (no shell, timeout, output cap)
                            -> post_probe (evidence recorded, redacted)

A tool that cannot be reached any other way cannot be used any other way.
"""
