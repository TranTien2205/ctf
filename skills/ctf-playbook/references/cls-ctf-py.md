# ctf.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

The entry wrapper - classify + dispatch in one call. Emits the
category and the router to open; it routes, never solves.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
