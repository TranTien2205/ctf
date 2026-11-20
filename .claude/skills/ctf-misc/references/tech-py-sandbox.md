# PyJail audit-sandbox escapes

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

sys.addaudithook hooks fire on open/import/exec - an audit-sandbox jail needs a different escape than a filter-only jail (the hook's events are the boundary).

## Pivot

Module read -> the shared file or class skill it names.
