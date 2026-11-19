# Multi-arena vs single — threaded services


A threaded service on a multi-CPU host uses several arenas — the same
size chunk freed from different threads lands in different bins.

## Consequences

- Grooming must know which thread/arena the corruption lives in.
- Cross-arena techniques (house of mind) need the fake arena setup.
- The tcache is per-THREAD — thread-local bins.

## Falsifier

The service is single-threaded: one arena — ignore arena complexity.
