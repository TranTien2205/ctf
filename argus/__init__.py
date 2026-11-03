"""argus — an evidence-gated, multi-model penetration-testing agent system.

Four planes, in dependency order:

    ledger/        the control plane: scope, state, proof, the only write path
    broker/        the tool plane: MCP servers in front of real pentest tools
    runtime/       the harness plane: one agent loop, one profile per model
    orchestrator/  the coordination plane: plan, route, schedule, verify

Nothing above the ledger may write a finding. Nothing above the broker may
run a command. Those two rules are what make the rest safe to automate.
"""

__version__ = "0.1.0"
