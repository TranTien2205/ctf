# The flush trigger — firing FSOP


FSOP needs a stdio call AFTER the corruption: exit(), fflush,
abort's stderr write, an error print — the trigger is the firing
condition.

## The triggers

- exit() → __run_exit_handlers → _IO_cleanup → flush.
- abort → stderr write.
- A direct fflush(NULL) in the service.
- A puts/printf on a corrupted FILE.

## Falsifier

No stdio call runs after the corruption: the write is dead — find a
trigger first.
