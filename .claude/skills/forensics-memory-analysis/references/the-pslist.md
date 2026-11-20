# pslist / pstree — the process inventory

`windows.pslist` lists EPROCESS entries in order; `windows.pstree`
indents by parent — the parent/child anomalies stand out (a
process spawned by a document, a svchost with the wrong parent).

## The trick

Sort by start time and look at the TAIL — challenge processes run
late and alone. A pslist full of svchosts is normal.
