# Whitebox hunt — finding the bug in source

When the handout includes source, the GraphQL bug is greppable. This file is
the source-review checklist — what to grep, where the bug hides in each
framework's idiom.

---

## 1. The universal greps

```bash
# resolvers that build queries by concatenation
grep -rnE '(query|execute|raw|sql|run).*(f"|\+\s|\$\{|`|concat)' --include='*.py' --include='*.js' --include='*.ts' --include='*.rb' --include='*.java' --include='*.go' --include='*.php' --include='*.ex' --include='*.exs' --include='*.rs' --include='*.cs'

# find/findOne/getById patterns that take the id from args
grep -rnE '(find|findOne|findById|findByPk|get|getById|getByPk|where|filter)\s*\(' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.java'

# the missing authz — resolvers without context.user / auth checks
grep -rnE 'resolve\([^)]*\)\s*{' -A5 --include='*.js' --include='*.ts' | grep -vE 'context\.(user|auth|session|request)|ctx\.(user|auth|session)'

# Object.assign / model.create on raw input
grep -rnE '(Object\.assign|Model\.create|new\s+\w+\(|set\(|update\(|insert\(|save\().*(args|input|params|data|fields)' --include='*.js' --include='*.ts' --include='*.py'

# mass-assign sinks
grep -rnE '(Object\.assign|Object\.merge|Object\.set|_\.merge|_\.set|merge\(|deepMerge|extend\()' --include='*.js' --include='*.ts' --include='*.py'

# the context the resolvers read
grep -rnE 'context\s*[.:]\s*(user|auth|session|request|viewer|me|currentUser)' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb'
```

## 2. Node/Apollo/express-graphql patterns

The idioms that carry the bug:

```javascript
// the concat-SQL resolver — find(`WHERE x='${args.q}'`)
const user = await db.query(`SELECT * FROM users WHERE name='${args.name}'`);

// the raw-find resolver — no authz
resolve: (parent, args, ctx) => db.users.findById(args.id)

// the ctx-trusted resolver — ctx.user set by middleware
resolve: (parent, args, {user}) => db.users.findById(user.id)

// the assign-from-input resolver — mass assign
resolve: (parent, {input}) => User.create(input)

// the merge-pollution resolver
resolve: (parent, {input}) => _.merge(user, input)

// the nested resolver without re-authz
Post: { author: (post) => db.users.findById(post.authorId) }
```

Grep targets in Node:

```bash
grep -rn 'resolve\|field\|type\|args\|ctx\|context\|input\|parent' \
  --include='*.js' --include='*.ts' | grep -v 'test\|spec\|mock'
grep -rn 'Object.assign\|_\.merge\|Model\.create\|\.update(\|\.findById\|\.findOne\|\.where(' --include='*.js' --include='*.ts'
grep -rn 'eval\|exec\|execSync\|spawn\|system\|shelljs' --include='*.js' --include='*.ts'
grep -rn 'require.*graphql\|ApolloServer\|graphqlHTTP\|createHandler' --include='*.js' --include='*.ts'
```

## 3. Graphene/Python patterns

```python
# the concatenated-query resolver
def resolve_user(root, info, name):
    return User.query.filter(f"name='{name}'").first()

# the raw-find resolver
def resolve_user(root, info, id):
    return User.get(id)

# the filter-set leak — the filter fields are the WHERE
class UserFilter(FilterSet):
    class Meta: model=User; fields=['username','email']

# the mutation that takes input kwargs
def mutate(root, info, **kwargs):
    user = User(**kwargs)   # every input field lands on the model
```

Grep:

```bash
grep -rn 'resolve_\|def resolve\|@field\|Field(' --include='*.py'
grep -rn 'filter\|get\|query\|WHERE\|execute\|raw\|format' --include='*.py' \
  | grep -v 'test\|migrations'
grep -rn '\*\*kwargs\|\*\*args\|User(\|Model(' --include='*.py'
```

## 4. graphql-ruby patterns

```ruby
field :user, Types::UserType, null: true do
  argument :id, ID, required: true
end
def user(id:)
  User.find(id)         # no authz — the bug
end

def user(id:)
  authorize User.find(id)  # Pundit — the check
end
```

Grep:

```bash
grep -rn 'def \|field \|argument ' --include='*.rb' | grep -v 'spec\|test'
grep -rn 'User\.find\|Model\.find\|\.where\|\.find_by\|\.find_by_id' --include='*.rb'
grep -rn 'authorize\|policy\|Pundit\|CanCanCan' --include='*.rb'
```

## 5. graphql-java patterns

```java
@DataFetcher
public DataFetcher getUser() {
  return env -> userRepo.findById(env.getArgument("id"));
  // no SecurityContext check — the bug
}
```

Grep:

```bash
grep -rn 'DataFetcher\|getArgument\|findById\|findByName' --include='*.java'
grep -rn 'SecurityContext\|@PreAuthorize\|@Secured\|@RolesAllowed' --include='*.java'
```

## 6. Absinthe/Elixir patterns

```elixir
field :user, :user do
  arg :id, non_null(:id)
  resolve fn _, %{id: id}, _ ->
    {:ok, Repo.get(User, id)}   # no authz
  end
end
```

Grep:

```bash
grep -rn 'resolve\|Repo\.get\|Repo\.all\|Repo\.find' --include='*.ex'
grep -rn 'context\.current_user\|Absinthe\.Plug\|@middleware' --include='*.ex'
```

## 7. Hasura patterns

Hasura is config, not code — read the metadata:

```bash
grep -rn 'x-hasura\|permissions\|role\|select\|insert\|update\|delete' \
  --include='*.yaml' --include='*.json' --include='*.yml' --include='*.toml'
```

The bug is a `check:{}` or a missing `filter` on a sensitive table's `select`
permission.

## 8. The resolver-to-sink map

For every resolver, draw the line to the sink:

```text
resolve_user(args.id)
  → ctx.user?   (authz check? — if absent, IDOR)
  → db.findById(args.id)
    → Mongo: find({_id:args.id})       — args.id object → NoSQLi
    → SQL:   WHERE id=args.id           — args.id string → SQLi
    → ORM:   findById(args.id)          — the ORM's coercion decides
    → File:  read("/uploads/"+args.id)  — args.id → path traversal
    → Shell: exec("find "+args.id)      — args.id → cmdi
    → HTTP:  fetch("http://api/"+args.id) — args.id → SSRF
```

The grep targets the *sink*, not the resolver — the resolver is just the
carrier.

## 9. The middleware file

`auth.js`/`middleware.ts`/`context.ts`/`server.ts` — find where `context.user`
gets set and which resolvers skip the check:

```bash
grep -rn 'context\s*=\|context:' --include='*.ts' --include='*.js' | head -20
grep -rn 'context\.' --include='*.ts' --include='*.js' | grep -v 'user\|auth\|session' | head -20
```

The *absence* of `context.user` reads in a resolver file is the signal —
that resolver doesn't authz.

## 10. The config file

`apollo-server` config, `express-graphql` options, `yoga` config — the
middleware order and the disabled features:

```bash
grep -rn 'introspection\|playground\|graphiql\|debug\|depth\|complexity\|csrfPrevention\|allowBatched\|maskedErrors' \
  --include='*.ts' --include='*.js' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.env' --include='*.config.*'
```

Defaults that matter: `introspection: false`, `playground: false`,
`debug: false`, `csrfPrevention: true`, `allowBatchedHttpRequests: false`,
`maskedErrors: true`, `depthLimit: N`, `complexityLimit: N`. The *absence*
of these is the attack surface.
