# Question: Question: which account created it

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

4697 `SubjectUserName`, TaskCache `SecurityDescriptor` SDDL (survives XML deletion), task XML `<UserId>` (who it RUNS as  -  not who created it), Sysmon 1/4688 of `sc create`/`schtasks /create`/New-Service. Distinguish the creator from the run-as.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.
