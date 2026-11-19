# Re-checking assumptions — the stale exploit


An exploit that worked last week may fail today: the libc changed, the
binary was rebuilt, the service restarted on a different image — re-
verify every assumption on re-run.

## The recheck list

- The libc file/version.
- The protections (rebuild may add PIE/RELRO).
- The menu ops (the service may have changed).
- The slot array size.

## Falsifier

Any assumption stale: re-derive before composing.
