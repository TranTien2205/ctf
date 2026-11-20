# Naming the suspect — the method

1. pslist, sort by start time — look at the tail.
2. Cross-check psscan — anything pslist missed (hidden).
3. pstree — odd parent/child.
4. cmdline — the odd argument/path.
5. netscan — the odd endpoint.
Each narrows. Record the PID + the plugin that named it.
