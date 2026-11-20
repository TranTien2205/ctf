# Triage before depth

Depth module for `ctf-reverse`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

file/readelf/strings/`pwn_triage.py` first - the binary's protections and imports pick the reading path BEFORE any deep dive: a stripped Go binary, a packed PE and a .pyc each route to different shared files.

## Pivot

Module read -> the shared file or class skill it names.
