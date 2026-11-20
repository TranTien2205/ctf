# Scenario: guarded endpoint

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself.

A guard model screens the chat - the payload must pass the guard's prompt AND the main model's refusal: two boundaries, usually one family crosses both.

## Pivot

Module read -> the family file or class boundary it names.
