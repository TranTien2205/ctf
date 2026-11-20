# Trap: content-type assumptions

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

An endpoint that accepts JSON may also accept form/multipart/XML - and each parser may differ (mass-assignment, XXE, parameter pollution). Test the content-type matrix before the payload.

## Pivot

Module read -> the shared file or class skill it names.
