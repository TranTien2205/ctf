---
argument-hint: "[challenge-name]"
---

Decide the next step for this challenge, from outside the agent: $ARGUMENTS

```bash
python3 tools/state.py $ARGUMENTS --show
python3 tools/decide.py $ARGUMENTS
```

`decide.py` returns exactly one action. Do that action, not the one that feels
more promising. It enforces what an agent judging its own progress will not:

- five probes or fifteen minutes in one class -> `switch_class`; park the branch
  at priority 0 with `tools/state.py --deprioritize`, change mechanism layer, and
  never try a sixth variant of the same idea
- a matching chain card -> run the card's probe before inventing a new one
- a confirmation with no confirming probe behind it -> it is reopened
- empty state -> classify first, probe second

Every probe verdict goes through the hooks, which are the only write path:

```bash
python3 tools/hooks.py pre-probe  <challenge> --request '<what you will send>'
python3 tools/hooks.py post-probe <challenge> --verdict confirms|refutes|inconclusive \
        --evidence '<verbatim excerpt of the response>'
```

A timeout or a connection reset is never a confirm. A write-shaped probe needs
`--write-ack` after reading the chain card's `blast_radius`.
