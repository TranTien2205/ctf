# Stack playbook: elixirphoenix

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Elixir/Phoenix: cowboy server header,
_phoenix_session cookie (signed), /live/ websocket routes,
absinthe /graphql common.

Recon checks:
- /live or ws upgrade -> Phoenix LiveView = server-driven UI
  (message-level surface)
- Plug parsers -> json+form+multipart acceptance
- ecto error shapes -> postgres/ecto identity
- /dev/dashboard -> Phoenix dev dashboard = telemetry +
  process map if exposed
- Absinthe endpoint -> graphql route

Predicts: websocket-surface classes, nosqli rare, sqli via
ecto raw, idor on ecto ids.
## Pivot

Signal harvested -> out-*; route named -> that skill.
