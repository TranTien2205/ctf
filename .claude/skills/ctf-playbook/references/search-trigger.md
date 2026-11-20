# When search fires

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

One named fact needed for the next probe is absent from all
supplied material - the fact is stated first (search_facts),
then searched narrowly. Absent means checked locally first.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
