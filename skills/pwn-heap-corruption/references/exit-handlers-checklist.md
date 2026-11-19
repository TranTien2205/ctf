# exit handlers and __run_exit_handlers — checklist

Companion to `exit-handlers.md`.

## Checklist

- [ ] exit() → __run_exit_handlers → _IO_cleanup → flushes FILEs → vtable
- [ ] tls_dtor_list / __pthread structures — newer writable call lists.
- [ ] A corruptible function-pointer slot the process registers.
