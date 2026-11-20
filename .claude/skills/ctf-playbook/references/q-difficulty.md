# Question: the time-box

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Easy 15-30, medium 30-60, hard 60-120 minutes - set before
the first probe, revisited at the stuck threshold. The box
is a tripwire, not a deadline.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
