# Step 0: black-box recon

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Entry page + front-end JS + endpoint list + stack
fingerprint - at most three commands before classifying.
Recon serves classification, not the other way.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
