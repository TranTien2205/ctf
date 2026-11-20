# Edge: Embedded/IoT logs

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Non-Windows bundles: /var/log rotation patterns, journald vacuuming, logrotate configs — 'cleared' on Linux is usually rotation or deliberate `> file` truncation. Shell history files are the PSReadLine analog.

## Pivot

`corpus-index.md`; the falsifier block for clean bundles.
