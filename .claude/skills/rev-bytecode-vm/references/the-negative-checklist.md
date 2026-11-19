# Negative results — what closed a thread — checklist

Companion to `the-negative.md`.

## Checklist

- [ ] The dispatch table was runtime-generated → static recovery dead;
- [ ] The check was a hash, not a compare → couldn't invert; the flag
- [ ] The .pyc was for a version with no marshal reader → needed xdis.
- [ ] The "VM" was actually an encoding chain → misc-encoding-carrier.
