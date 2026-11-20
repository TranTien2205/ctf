# Step 0: classify

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

ctf.py --json on the observation or --source on the handout -
the classifier's category is the router decision. One call,
one category.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
