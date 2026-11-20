# Split by probe, not by name

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

Two classes share a family when ONE probe distinguishes them - sqli
and nosqli share because one request decides string-vs-object. The
grouping is probe-shaped; the family names are just labels.

## Pivot

Module read -> the sibling module the question names, or back to the
SKILL.md procedure.
