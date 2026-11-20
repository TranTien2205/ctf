# Route: chan-slow-dribble

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Base module: `chan-slow-dribble.md` carries the detection stack; this card points where its confirmation feeds.

## Primary question

`q-long-session.md`.

## Depth partner

`q-single-peer-volume.md`.

## Confirm shape

A channel is confirmed by a quoted row showing its tell AND its direction/volume — one without the other is a lead.

## Pivot

Channel tell absent -> the next channel in `corpus-index`; all channels absent -> the falsifier block in `../SKILL.md`.
