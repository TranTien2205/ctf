# Contest phases

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

First 30% sweep easy and bank points; middle 50% mediums plus
hards with an existing idea; last 20% verify and submit only.
The last phase never opens a new direction.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
