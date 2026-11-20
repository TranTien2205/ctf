# Signal cell: person / rev

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Whether the observed signal `person` routes to the `rev` row of the entry table.

## Read

Strong-raise, weak-raise, neutral, or rules-out for this row -
one line of reasoning. The table maps the STRONGEST observed
signal; a weak-raise cell is corroboration, not the route.

## Router

`../../rev-triage/` when this row wins - only when the
signal is the strongest one observed.
