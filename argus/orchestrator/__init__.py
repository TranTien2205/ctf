"""The coordination plane — the part that makes several models one tester.

Four pieces, and the order matters:

    bus.py        the shared context: decisions, events, briefs, reports, on disk
    planner.py    one strong model turns an objective into tasks, and stops
    workflows.py  reusable plan templates, so a shelf plan and a model plan are
                  the same artifact and can be compared
    router.py     each task gets a runner, a model and a mode, by strength and cost
    scheduler.py  a ready queue and fixed slots; a free slot is filled at once
    runner.py     three ways to execute one task: our harness, claude, opencode
    verify.py     a model from another family reads the evidence before it ships
    metrics.py    reads the instrumentation back: probes, refusals, cost per finding

The thing that does not exist here is a model that "understands the whole
context". Nothing does. What exists is a plan on disk, a decisions store any
agent can read, and a ledger that every tool call writes to — so an agent that
joins at task nine knows what the first eight established without having been
in the conversation.
"""
