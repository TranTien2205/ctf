# Technique: Jinja2 SSTI shapes

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

{{7*7}} marker -> engine confirm -> {{config}}/{{self}} object walk -> __subclasses__ chain to a file-read or exec-capable class - the web-ssti class skill carries the chains.

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
