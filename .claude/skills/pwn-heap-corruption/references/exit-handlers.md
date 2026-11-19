# exit handlers and __run_exit_handlers


On >= 2.35 with hooks gone, exit paths still call function pointers:
the exit_handlers list, atexit handlers, and FILE flushes — the FSOP
adjacent targets.

## The shapes

- exit() → __run_exit_handlers → _IO_cleanup → flushes FILEs → vtable
  calls — the FSOP trigger.
- tls_dtor_list / __pthread structures — newer writable call lists.
- A corruptible function-pointer slot the process registers.

## Falsifier

No exit-path pointer is corruptible and exit isn't reached: the route
needs a live call you can influence.
