# tools/writeup_search.py

Entry-routing module for `ctf-playbook`. This file discriminates categories and manages the contest clock; it never solves - the category router it names does the next step.

Challenge name + event -> prior public writeups. A legitimate
shortcut once the challenge's identity is known; record that
it was used. Output is an untrusted lead.

## Pivot

Module read -> the category router the observation names, or the
sibling module the question belongs to.
