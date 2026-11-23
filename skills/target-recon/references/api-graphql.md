# API recon: graphql

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

GraphQL recon: GET+POST on /graphql /graphiql
/playground /altair /v1/graphql /api/graphql. Introspection
probe {__schema{queryType{name}}} - 200 with types = full
map available; 'introspection disabled' = field-guessing via
suggestion errors instead. Batching/alias behavior and
persisted-query headers recorded as surface notes.
## Pivot

Signal harvested -> out-*; route named -> that skill.
