# Worked example: graphql

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: JS bundle showed /graphql.

1. GET /graphiql -> 200 IDE page = introspection posture hint.
2. api-graphql probe: POST {"query":"{__schema{queryType{name
   }}}"} -> 200 types list = full schema (dx2-introspectionon).
3. Mutations list -> registerUser, updateProfile fields =
   massassign/idor surfaces; node(id) relay pattern -> idor
   prior (cls-idor needs id shape).
4. Observations: introspection ON, 14 mutations, node() ids
   base64-shaped.
5. Route: web-graphql depth skill with the schema in hand.
## Pivot

Signal harvested -> out-*; route named -> that skill.
