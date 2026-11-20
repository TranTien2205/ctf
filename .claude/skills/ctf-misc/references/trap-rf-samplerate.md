# Trap: wrong sample rate assumed

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

The capture's sample rate bounds what can be demodulated - a 2MHz capture can't carry a 20MHz-wide signal; check the header metadata before demod attempts.

## Pivot

Module read -> the shared file or class skill it names.
