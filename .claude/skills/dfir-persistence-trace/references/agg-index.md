# Aggregator: Corpus index

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Families: `svc-*` service records and hive keys; `task-*` task XML, TaskCache, DynamicInfo, scheduler events; `run-*` registry autostart; `wmi-*` subscriptions; `misc-*` startup/Office/BITS; `lnx-*` systemd/cron/keys; `mac-*` launchd; `q-*` question shapes; `meth-*` sweep methods; `trap-*` falsifier traps; `scen-*` bundle scenarios; `deep-*` decoded internals; `sig-*` operator-side signatures; `tool-*` tool routes; `mx-*` mechanismxquestion cells; `work-*` discipline.

## Use

An index  -  open the named family module for the artifact detail; this
file only decides which one.

## Pivot

Index consulted -> the module it names.


## Closing note

Record the reading, not the impression: the corpus exists so that a
verbatim record or a recorded negative  -  not a hunch  -  ends each probe.
