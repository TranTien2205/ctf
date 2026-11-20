# Registry: regipy transaction replay

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Signature: `apply_transaction_logs(hive_path, primary_log_path, secondary_log_path=None, restored_hive_path=None)` — there is NO `transaction_log_path` parameter; passing one is a real signature error. regipy is rank 4 in `skills/dfir-sherlock-triage/toolchain.md` and absent here; `artifact_inventory.py` still names the family `registry-transaction-log`.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
