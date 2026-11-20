# Technique: php://filter LFI

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

php://filter/convert.base64-encode/resource=<file> reads source through the include - the standard first read; iconv/charsets variants for filters that block base64.

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
