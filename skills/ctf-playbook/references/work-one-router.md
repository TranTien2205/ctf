# Open exactly one router

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Classify, then open exactly one category router - never two to
compare. A wrong router costs one re-run of skill_select; two open
routers anchors the whole session.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
