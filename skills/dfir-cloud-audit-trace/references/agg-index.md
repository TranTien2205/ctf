# Aggregator: Corpus index

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Families: `ct-*` CloudTrail envelope+fields; `ui-*` userIdentity; `api-*` action patterns; `s3-*` server access log; `gd-*` GuardDuty; `vpc-*` flow logs; `ent-*`/`m365-*`/`okta-*`/`gw-*` other providers (UNVERIFIED); `ev-*` per-eventName field cards; `fld-*` field tables; `q-*` question shapes; `meth-*`/`trap-*`/`scen-*`/`deep-*`/`tool-*`/`work-*`/`neg-*`/`rec-*`/`cross-*`; `mx-*` artifact x question cells.

## Use

An index - open the named family module for the detail; this file
only decides which one.

## Pivot

Index consulted -> the module it names.
