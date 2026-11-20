# Deep dive: Deep: federated types

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

SAMLUser/WebIdentityUser on AssumeRoleWithSAML/WithWebIdentity - `.userIdentity.principalId` and the IdP attributes in sessionContext carry the federated identity; the 'username' is not a userName field.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
