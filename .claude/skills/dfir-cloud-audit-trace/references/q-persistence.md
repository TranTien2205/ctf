# Question: Question: persistence planted

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

CreateAccessKey on an existing user, CreateUser+AttachUserPolicy pair, CreateLoginProfile on a key-only user, UpdateAssumeRolePolicy widening a trust, new IAM role with a broad assume policy - each is a persistence artifact, not just an action.

## Answer shape

eventTime + eventName + the verbatim field the question asked for +
which artifact (trail/access log/flow) it was quoted from.

## Pivot

Question not in the cloud plane -> `cross-*` to the host or network
class.
