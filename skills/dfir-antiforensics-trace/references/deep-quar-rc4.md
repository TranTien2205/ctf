# Deep: The RC4 obfuscation, precisely

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

256-byte key hardcoded in mpengine.dll, first bytes `1E 87 78 1B 8D BA A8 44 CE 69` (ernw/quarantine-formats). Every chunk in the store uses it — Entries files, ResourceData, Resources. It's obfuscation not encryption: the same key every install, so any RC4 implementation with that keystring decrypts.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
