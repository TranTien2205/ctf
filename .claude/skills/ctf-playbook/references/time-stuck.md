# The stuck rule

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Past ~15 minutes stuck: re-read the brief for a missed hint,
change mechanism layer, then park and return. Sitting on one
challenge is the classic contest loss.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
