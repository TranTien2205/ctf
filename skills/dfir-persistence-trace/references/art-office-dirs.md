# Module: Artifact: Office autostart dirs

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Word STARTUP (.wll), Excel XLSTART (.xll/.xlam), Templates\Normal.dotm  -  template macros fire on document open; olefile lists the streams; a macro stream in Normal.dotm is the record.

## Evidence rule

Artifact/field modules name WHERE the record lives and what it is
called  -  the verbatim quote is still the claim's evidence.

## Pivot

Module read -> its matching `*-route` card for the next step.
