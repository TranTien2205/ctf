# Stack playbook: graphqlsvc

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

GraphQL service: /graphql /graphiql /playground
/altair /v1/graphql (Hasura) endpoints; POST JSON {query:...}.

Recon checks:
- GET /graphiql /playground -> IDE surface = schema UI
- Introspection {__schema{types{name}}} -> full type map =
  every query/mutation + arg = complete surface
- Field suggestions ('Did you mean') -> typo-probing names
- Persisted-query only mode -> different recon path
- Batching + alias abuse surface notes

Predicts: graphql class depth skill; idor via node(id) relay
pattern, injection through resolver args, authz on mutations.
## Pivot

Signal harvested -> out-*; route named -> that skill.
