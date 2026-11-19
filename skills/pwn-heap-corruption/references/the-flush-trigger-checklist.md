# The flush trigger — firing FSOP — checklist

Companion to `the-flush-trigger.md`.

## Checklist

- [ ] exit() → __run_exit_handlers → _IO_cleanup → flush.
- [ ] abort → stderr write.
- [ ] A direct fflush(NULL) in the service.
- [ ] A puts/printf on a corrupted FILE.
