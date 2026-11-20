# Technique: Twig SSTI shapes

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

{{_self.env}}/{{_context}} escapes, dump() for enumeration - PHP-world counterpart to Jinja; the engine-id marker differs ({{7*'7'}} -> '7777777' in Twig, '49' in Jinja2).

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
