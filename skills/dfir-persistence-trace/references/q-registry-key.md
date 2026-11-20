# Question: Question: which registry key was modified

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Answer = full path from the HIVE root + value name + verbatim data. ControlSet resolution first (`Select\Current`)  -  answering `ControlSet002` when the live set is 001 is a wrong answer even if the path is otherwise right.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.
