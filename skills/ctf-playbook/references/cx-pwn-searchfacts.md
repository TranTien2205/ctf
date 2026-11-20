# Cell: pwn / tools/search_facts.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Whether `tools/search_facts.py` runs at the `pwn` route.

## Read

Which control-plane tool the category's step-0 calls and in what
order - classify and chain_match always run; the rest depend on
what the handout supplies (source, lockfiles, prior attempts).

## Note

The tool emits candidates and decisions; the category router
owns the first probe. A tool's output is never the solve.
