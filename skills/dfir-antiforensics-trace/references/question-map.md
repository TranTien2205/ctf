# Question map

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Route the phrased question to its module before probing.

| Question shape | Open first | Then |
|---|---|---|
| when were the logs cleared | `q-when-cleared.md` | `evt-1102.md` |
| who cleared them | `q-who-cleared.md` | `evt-1102.md` |
| which log | `q-which-log.md` | `evt-104.md` |
| records surgically deleted | `q-records-deleted.md` | `evt-record-id-gaps.md` |
| how many records/when | `q-gap-bounds.md` | `deep-gap-arithmetic.md` |
| what command did it | `q-clear-command.md` | `sig-wevtutil-cl.md` |
| which channels were hit | `q-which-channels-hit.md` | `deep-channel-scope.md` |
| service killed | `q-service-killed.md` | `evt-sysmon4.md` |
| audit policy gutted | `q-policy-gutted.md` | `evt-4719.md` |
| Sysmon tampered | `q-sysmon-killed.md` | `evt-sysmon4.md` |
| file timestomped | `q-file-timestomped.md` | `ts-si-fn-divergence.md` |
| what was deleted | `q-what-deleted.md` | `del-sysmon23.md` |
| wiped or deleted | `q-wiped-vs-deleted.md` | `del-sdelete.md` |
| shredder name | `q-shredder-name.md` | `del-sysmon28.md` |
| Defender blinded | `q-was-defender-blinded.md` | `def-5007.md` |
| what was excluded | `q-exclusion-scope.md` | `def-exclusions.md` |
| who set the exclusion | `q-who-set-exclusion.md` | `reg-sysmon-12-14.md` |
| shadows deleted | `q-shadows-killed.md` | `vss-delete.md` |
| journal deleted | `q-journal-killed.md` | `vss-usn-delete.md` |
| registry value hidden/deleted | `q-registry-hidden.md` | `reg-logs-version.md` |
| PS history deleted | `q-history-file-deleted.md` | `deep-psreadline.md` |
| sample recoverable | `q-sample-recoverable.md` | `qar-workflow.md` |
| log file intact | `q-log-integrity.md` | `tool-gap-probe.md` |
| pre-clear content | `q-pre-clear-content.md` | `vss-recovery.md` |
| what Defender saw | `q-detection-missed.md` | `qar-mplog.md` |
| was it erased at all | `meth-two-answers.md` | `meth-falsifier.md` |

## Using the map

Left column is how bundle questions are phrased. Middle is the procedure;
right is the first record it reads. Dry after three shapes -> the recovery
table (`rec-*`) for whatever the answering artifact's state is.
