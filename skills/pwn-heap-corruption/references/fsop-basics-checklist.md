# FSOP — file stream oriented programming — checklist

Companion to `fsop-basics.md`.

## Checklist

- [ ] Works where hooks are gone (glibc >= 2.34).
- [ ] exit() and fflush drive the call — a reachable trigger.
- [ ] _IO_2_1_stderr_, _IO_2_1_stdout_, _IO_2_1_stdin_ have known libc
- [ ] 1. Arbitrary write → overwrite a FILE's vtable pointer or a jump entry
- [ ] 2. Trigger the stdio call — exit(), fflush(NULL), a print error path.
- [ ] 3. The call dereferences your forged pointer → PC control.
- [ ] 2.24+: vtable check `_IO_vtable_check` — the vtable must point inside
