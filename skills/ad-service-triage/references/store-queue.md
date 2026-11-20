# Flag store: queue/cache

Method module for `ad-service-triage`. Attack-defense
service intake: find the flag store, the paths reaching it,
what the checker needs - in contest order, not jeopardy
order. Availability is scored; the flag rotates every tick.

Redis/memcached/queue holding the flag - paths
are the queue consumers and any exposed admin.

## Exit

Named next step -> that module.
