# Negative results — what closed a thread

- The dispatch table was runtime-generated → static recovery dead;
  traced instead.
- The check was a hash, not a compare → couldn't invert; the flag
  wasn't recoverable from the bytecode alone.
- The .pyc was for a version with no marshal reader → needed xdis.
- The "VM" was actually an encoding chain → misc-encoding-carrier.
