# PyJail frame walking

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

sys._getframe()/inspect.currentframe() climbs the call stack to reach globals the local scope lacks - the frame's f_globals is the escape target.

## Pivot

Module read -> the shared file or class skill it names.
