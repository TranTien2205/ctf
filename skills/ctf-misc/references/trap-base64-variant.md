# Trap: base64 variant assumed

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

base64url swaps +/ for -_; base64 in a URL or JWT is often the url variant - the wrong alphabet yields garbage that still decodes partially.

## Pivot

Module read -> the shared file or class skill it names.
