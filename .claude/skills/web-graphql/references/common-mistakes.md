# Common mistakes — the GraphQL failure modes

The things that waste probe budget or produce false signals.

---

## 1. Treating schema disclosure as the finding

`{__schema{types{name}}}` returning data is *capability*, not harm — the
finding is the unauthorized read/mutation that follows. `post-probe
--verdict confirms --evidence-kind class` for the schema; `impact` only for
the leaked data itself.

## 2. Assuming introspection-off = safe

`__schema` blocked closes one channel. `_service{sdl}`, `__type(name:)`,
field-suggestion errors, the JS bundle, and the WS channel all still leak
the schema. Record the *specific* channel that closed, not the class.

## 3. Confusing `Cannot query field` for authz

`Cannot query field "admin"` means the field *doesn't exist* on the type —
not that it's protected. `Forbidden`/`Not authorized` means the field
exists and was checked. Two different bugs.

## 4. Missing the field-level authz escape

`user(id)` returns `Forbidden` — but `post(id){author{email}}` resolves the
same `User` type without the check. The authz lives on the *entry resolver*,
not the type. Always try the nested path.

## 5. Ignoring `data` + `errors` partial responses

`{"data":{"user":{"name":"x","email":null}},"errors":[Forbidden at email]}` —
email was authz'd, but name was not. Per-field authz: read each field's
status individually. The partial response is the *map* of what's checked.

## 6. Probing with the same identity

Cross-tenant reads need two identities — register twice, probe as both.
`user(id:2)` returning data proves nothing if `id:2` is *you*.

## 7. Accepting the first error shape

`Cannot query field "userss"` is *one* error shape. `argument "id" required`
is another. `Cannot return null` is a third. Each is a different signal —
learn all three before judging a field's status.

## 8. Sending invalid GraphQL to test for injection

`{user(name:"'"){id}}` — a quote inside a GraphQL string is legal GraphQL.
The quote reaching SQL is the *app's* problem, not the parser's. Don't
sanitize for the server — send it raw.

## 9. Forgetting the variables channel

`{"query":"query($x:String){f(x:$x)}","variables":{"x":"' OR 1=1--"}}` —
the injection rides `variables`, not the `query` document. WAFs that inspect
`query` miss it entirely.

## 10. Sending objects where strings are declared

`{"query":"{f(id:$x)}","variables":{"x":{"$ne":null}}}` — a scalar-declared
arg receiving an object is a type-confusion test, not an error. Some
validators pass it through → NoSQLi surface opens.

## 11. Treating depth-limits as authz

`Query depth limit exceeded` is a *cost* limit, not a check. The same field
reached through aliases/batching/a flatter shape still resolves.

## 12. Forgetting GET and form transports

`POST+JSON` is not the only carrier. `?query={...}` and
`query=...&variables=...` carriers are CSRF-relevant — and sometimes the
*only* carriers an authz middleware missed.

## 13. Probing only `node()` when `nodes()` exists

`nodes(ids:[...])` takes an array — one request, N ids, one HTTP log entry.
The batch surface is cheaper than per-id probes.

## 14. Not trying `__type` when `__schema` is blocked

`{__type(name:"Query"){fields{name}}}` is a separate field — a middleware
that strips `__schema` often leaves `__type`. Type-by-type introspection is
slow but works.

## 15. Ignoring deprecated fields

`fields(includeDeprecated:true)` — deprecated fields still resolve and are
usually older code with fewer checks. Always pull them.

## 16. Sending one query when batching is live

Array batching `[{...},{...},{...}]` or aliased docs multiply the probe
rate past per-request rate limits. If the server accepts either, use it.

## 17. Firing mutations before understanding write semantics

`mutation{deleteAll}` on a shared instance — the safety rule applies: probe
write effects on objects you created. `updateUser(id:SELF, ...)` proves the
primitive; `updateUser(id:1, ...)` proves the IDOR — do both, in order.

## 18. Confusing the error for the evidence

`errors[].message` containing `"flag{...}"` is the flag *if* it came from
the response — but it may also be a *decoy* the resolver throws to
misdirect. `pre-flag` requires the value be in the response — quote the
full response, not just the flag-shaped substring.

## 19. Stopping at the first field failure

`email` denied → try `token`, `role`, `sessions`, `apiKey`, `passwordHash`,
`salt`, `secret`, `mfa`, `ssn`, `phone`, `dob`, `address`, `balance`,
`credits`, `permissions`, `settings`, `preferences`, `privateNotes`,
`secretNotes`, `flags`. A type's private set is rarely one field.

## 20. Missing the `_service{sdl}` bypass

`__schema` blocked → try `_service{sdl}` — federation resolvers survive
`disableIntrospection` middlewares. Single most common bypass on Apollo
deployments.

## 21. Forgetting the WS channel exists

`subscription` types in the schema mean a WS endpoint — often a *different
server instance* with different middleware. The `subscription{}` type list
is the hint; `ws://`/`wss://` path is the target.

## 22. Treating `data:null` as failure

`{"data":{"user":null}}` + no errors means the resolver ran and returned
null — different from `Cannot query field` (didn't exist) or `Forbidden`
(checked). Null is "exists but filtered/absent" — the field is real.

## 23. Missing the enum-value wordlist

`enum Role {USER ADMIN SUPER_ADMIN STAFF}` — the enum values are the arg
wordlist for mass-assign and the schema's own privilege map. Read every enum.

## 24. Assuming the `id` arg type limits enumeration

`id:ID` accepts strings *and* ints — `"1"`, `1`, `"01"`, `"1.0"`, `"1e2"`,
`" 1"`, `"1 "`, `"+1"`, `"0x1"` may all resolve to the same object.
Canonicalization bugs are the ownership-bypass surface.

## 25. Recording what you sent, not what came back

`post-probe --evidence` wants the *response bytes* — the server's own words.
Re-typing `email was leaked` isn't evidence; `"email":"victim@x.tld"` quoted
from the response body is.

## 26. Skipping the authz-matrix when introspection is off

No schema ≠ no authz map. The suggestion oracle + `did you mean` hints
recover the field names — then the same two-role diff applies. Introspection-
off is a recon problem, not a pass on authz testing.

## 27. Using the same probe shape every time

`{user(id:N){email}}` for N=1..10 — fine. But also try `users{email}` (list),
`node(id:)` (global), `search(q:)` (injection path), `post.author{email}`
(nested), `_entities(User:id)` (federation path). Same field, six carriers —
each has different middleware.

## 28. Forgetting the ordering probe

`{user(){id}}` — *omitted* arg. The resolver's default path runs — often
`find all` or `find first` — a free list when `id` was the only check.

## 29. Not checking what the response *excluded*

```json
{"data":{"user":{"name":"x","role":null,"sessions":null}},
 "errors":[Forbidden on role, Forbidden on sessions]}
```

The `null`s + the `path` array name *which* fields are checked — the diff
between null and data is the authz surface.

## 30. Ignoring the timing channel entirely

When everything else is masked, timing still separates: exists vs not,
valid vs error, true vs false. `blind-graphql.md` covers the oracles —
a resolver that *sleeps* on a condition is a signal that carries a bit.
