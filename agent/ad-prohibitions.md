## PROHIBITED - these are not preferences

1. Never send a request to a host that is not listed, individually, in the
   team list of the flag_farm config for this service. No range, no sweep, no
   adjacent address, no organiser infrastructure, no host you inferred from a
   hostname pattern. Do not work around the config guard, and do not add a
   host the operator did not type.
2. Never delete, move, truncate, rename or overwrite an artifact, a log, a
   capture, a backup or a ransom note. Availability can be restored; evidence
   cannot. If something has to be moved, name it and stop.
3. Never edit a file inside a service directory unless a snapshot from
   tools/ad/sla_check.py --save exists for that service, was written in the
   last ten minutes, and you have quoted its "passed" and "checks" numbers in
   your report. After the edit, run sla_check.py again with --compare against
   that snapshot. If comparison.regressions is not empty, write REVERT THE
   PATCH, restore the bytes you replaced, re-run --compare, and stop.
4. Never restart, stop, reload, redeploy or reinstall a service, and never
   restore a snapshot or a backup. You do not own availability. Print the
   command you would have run and stop. If you changed a file that needs a
   restart to take effect, say in your report that the change is NOT LIVE.
5. Never rotate, change or generate a credential, key, token or secret. Name
   the one you found, say where, and stop.
6. Never claim a flag. A flag counts only when it appears in a response body
   or in a supplied artifact, and only tools/ad/flag_farm.py submits one. Do
   not put a flag in a report, a commit message, a chat line, or any file
   outside the run directory.
7. Never state a finding without a path and a verbatim excerpt of the bytes
   that prove it. "Likely", "probably", "appears to" and "should be" are
   hypotheses: write HYPOTHESIS in front of them.
8. A timeout, a connection reset, an empty response or a missing input file is
   not a result. Record it as inconclusive, say which input was missing, and
   stop that item. Do not retry it a third time.
9. Stop at your stop condition and report. Do not start a different kind of
   work because the first kind ran out, and do not run the same tool again
   with different flags hoping for a better answer.
