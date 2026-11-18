# Directives — @skip/@include, custom directives, and authz annotations

Directives are GraphQL's annotation system — `@deprecated`, `@skip`,
`@include`, `@specifiedBy`, plus custom ones like `@auth`, `@hasRole`,
`@cost`, `@constraint`. Two attack surfaces: the *built-in conditional
directives* give the client free runtime control over execution, and *custom
directives* declare authz/cost that may or may not be enforced.

---

## 1. @skip and @include — client-controlled execution

Per spec, any field accepts `@include(if:)`/`@skip(if:)` — **the client
decides** which fields execute. Attacks:

```graphql
# conditional oracle — boolean split inside the document
query($c:Boolean!){ user{ name email @include(if:$c) } }
variables: {"c":true}  vs {"c":false}
```

The response *shape changes with the variable* — an in-document oracle that
can wrap expensive fields behind a condition driven by... an injected arg:

```graphql
# drive @include with an injected value? variables only —
# but combined with a SQL-injectable arg, the ORACLE pattern is:
query($n:String!){
  user(name:$n){
    id
    email @include(if:true)      # toggle point
  }
}
```

The real use: **strip fields mid-document without re-editing** — leave
`email @include(if:$c)` in and flip `$c` between requests.

## 2. Custom directive surface — read the SDL

```graphql
{__schema{directives{name locations args{name type{name}}}}}
```

Interesting custom directives:

```text
@auth / @hasRole / @isAuthenticated / @requiresScopes / @requires
@hasPermission / @access / @guard / @acl
@rateLimit / @cost / @complexity
@deprecated / @preview
@key / @external / @provides          # federation — federation.md
@connection / @client / @export       # client-side directives — harmless
@constraint / @validate / @length    # input validation
@cacheControl / @cache
@computed / @live / @defer / @stream  # execution modifiers — probes below
```

`locations` tells where they apply: `FIELD_DEFINITION`, `FIELD`, `OBJECT`,
`ARGUMENT_DEFINITION`, `INPUT_FIELD_DEFINITION`. `@auth` on `FIELD_DEFINITION`
is a *declaration* — read whether it's *enforced* by probing the field.

## 3. The dead-directive pattern

`@auth` declared in SDL but not wired to a directive implementation =
decorator that does nothing:

```graphql
type Query @auth(requires: ADMIN) {
  users: [User]           # annotated — try it anyway
}
```

Probe `{users{email}}` as a low-priv token — if it resolves, the directive
was never enforced. Common in: hand-written schemas where directives exist
for docs only, gateway setups where authz was "supposed" to live at the
gateway but never got wired.

## 4. @defer / @stream — incremental delivery tricks

Apollo/Relay incremental directives return data in multipart chunks:

```graphql
{ user { name ... on User @defer { email } } }
```

Attacks:

- **Partial-data authz**: authz checks run on the primary payload; deferred
  fragments sometimes skip a second check — the deferred fragment's fields
  resolve without re-verification.
- **Parser differentials**: the incremental multipart response format
  (`Content-Type: multipart/mixed`) confuses some WAFs/loggers — bypass.
- **Timing split**: deferred chunks reveal *when* a resolver ran — a timing
  channel even when the value is withheld.

## 5. @deprecated — the forgotten surface

```graphql
{__type(name:"Query"){fields(includeDeprecated:true){name isDeprecated}}}
```

Deprecated fields still resolve — they're *usually* older, less-maintained
code: the classic CTF shape is `userDetails` (deprecated) which predates the
authz that `user` got. Pull `includeDeprecated:true` on *every* type —
deprecated fields are low-hanging fruit by definition.

## 6. @specifiedBy and custom scalar leaks

`@specifiedBy(url:)` on a scalar names its format spec — the URL sometimes
points at internal docs: `https://internal-wiki/specs/custom-scalar` leaks
internal hostname.

## 7. Directive arguments as injection points

Directives taking args can reach resolvers:

```graphql
{ user @cacheControl(maxAge:999999) {email} }
{ search @live(q:"x' OR 1=1--") {name} }
mutation{ update @constraint(min:0, max:-1) {ok} }
```

`@cacheControl(maxAge:...)` drives server caching — a high maxAge caches a
*victim's* private response if the cache is shared (`web-cache-poisoning`).

## 8. Input-field directives

`@constraint`, `@validate` on `INPUT_FIELD_DEFINITION` declare input
validation. Their *absence* on a sensitive input field (say `role:` accepts
arbitrary strings vs `email:` validated) tells you which arg to target for
mass assignment. Read the SDL for the asymmetric validation — the unvalidated
fields are the targets.

## 9. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "deprecated field userDetails resolves where user() is authz-checked"
```

The directive itself is never the finding — it's a *map* to the fields the
author marked and the fields the author forgot.
