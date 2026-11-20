# Technique: SSRF gopher shape

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

gopher://<host>:<port>/_<urlencoded-tcp> - raw TCP through the fetcher: Redis/Memcached/MySQL writes are the classic targets; encoding the payload body is the fiddly part.

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
