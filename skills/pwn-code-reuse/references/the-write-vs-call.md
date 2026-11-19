# Write vs call — which ends the exploit


- A write primitive (GOT overwrite, hook write, pointer forge): the
  redirect happens at a LATER call — the write itself doesn't exec.
- A call primitive (ret to a function): the exec happens at the call.

The ending's shape decides which primitive the exploit needs.
