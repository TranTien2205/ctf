# Question: Question: how did the attacker maintain access

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

The umbrella phrasing. Answer = mechanism name + verbatim record: e.g. 'a service `helpsvc` with `ImagePath=C:\Users\Public\svc.exe` on a 7045 at <ts>'. Order: 7045 on System -> TaskCache+Tasks XML -> Run keys (all hives) -> WMI OBJECTS.DATA strings -> Linux/macOS only if the bundle is not Windows.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
