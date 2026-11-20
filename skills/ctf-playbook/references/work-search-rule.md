# The search rule

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Search when one named fact for the next probe is absent from
supplied material - search_facts.py states the missing fact
first. A new challenge is a reason to search narrowly, not to
avoid search.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
