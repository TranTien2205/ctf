# Bash xtrace/debug leaks

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

set -x inside a jail leaks the evaluated command to stderr - the debug channel shows what the filter let through.

## Pivot

Module read -> the shared file or class skill it names.
