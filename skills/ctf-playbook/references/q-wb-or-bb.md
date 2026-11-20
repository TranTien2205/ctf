# Question: white-box or black-box

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Source supplied -> classify.py --source reads constructs;
observation only -> classify.py on the observed text. The
carrier decides the command, not the category.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
