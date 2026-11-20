# Closing checklist

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

Before the claim leaves this class:

- the context identified (HTML body, attribute, JS string,
  DOM sink) with the verbatim reflection
- the sanitizer boundary measured (which bytes survive)
- the proof-of-execution evidence (the bot-visible marker or
  the exfil record), not just a rendered payload
- the encoding/bypass variant that landed vs refused ones
- the falsifier status explicit

## Pivot

Checklist complete -> record via hooks; incomplete -> the named gap.
