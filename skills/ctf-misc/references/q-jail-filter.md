# Question: what did the filter take

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Blocked chars (quotes, dots, letters) vs blocked words (eval, exec, import) vs blocked builtins - each maps to a different escape family: char reconstruction, word fragmentation, or attribute walks. The rejection messages name which.

## Pivot

Module read -> the shared file or class skill it names.
