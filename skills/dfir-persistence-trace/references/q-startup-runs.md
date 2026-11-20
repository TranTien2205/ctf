# Question: Question: what runs at startup

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Enumerate EVERY family, not one: services (Start 0-2), tasks with BootTrigger/LogonTrigger, Run/RunOnce + Policies Run, Winlogon values, AppInit/BootExecute, startup folders, WMI subscriptions, systemd units+cron on Linux. The answer is a LIST with the record for each, not the first suspicious item.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.
