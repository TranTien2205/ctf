# Step 0: source scan

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

White-box: routes, inputs, sinks, auth boundaries, queries,
flag path with file:line - before any payload. The scan is
the white-box recon.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
