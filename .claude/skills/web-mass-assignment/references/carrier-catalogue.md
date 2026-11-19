# Carrier catalogue — every delivery shape for the extra field

## JSON body carriers

```json
{"role":"admin"}                          ← flat
{"profile":{"role":"admin"}}              ← nested depth-1
{"a":{"b":{"role":"admin"}}}              ← nested depth-2
{"roles":["admin"]}                       ← array
{"groups":[{"id":1}]}                     ← array-of-objects
{"role":"user","role":"admin"}            ← duplicate key
{"role":null}                             ← null — clear or bind
{"role":""}                               ← empty string
{"role":true}                             ← boolean
{"role":1}                                ← integer
{"role":1e6}                              ← exponential
{"user":{"role":"admin"}}                 ← model-prefixed object
{"settings":{"admin":true}}               ← settings parent
{"metadata":{"role":"admin"}}             ← metadata parent
{"preferences":{"is_admin":true}}          ← preferences parent
{"billing":{"price":0}}                   ← billing parent
{"profile_attributes":{"role":"admin"}}    ← Rails nested-assoc
{"membership":{"role":"admin"}}            ← association parent
```

## Form-encoded carriers

```
role=admin                                ← flat
user[role]=admin                          ← Rails/PHP nested
user[profile][role]=admin                 ← depth-2 nested
user[profile_attributes][role]=admin      ← nested-assoc
role[]=admin                              ← array
roles[]=admin&roles[]=superuser           ← multi-element
groups[][id]=1&groups[][id]=2             ← array-of-objects
user.role=admin                           ← dotted qs
User.Role=admin                           ← .NET convention
role=user&role=admin                      ← dup (first-vs-last)
profile[settings][admin]=true             ← nested settings
membership[role]=admin                    ← nested association
role_ids[]=1&role_ids[]=2                 ← FK array
```

## Query-string carriers

```
POST /users?role=admin                    ← params union on write
GET  /users?role=admin                    ← mutating GET
PATCH /users/me?role=admin                ← params union
POST /orders?price=0&status=shipped       ← multi-field
```

## Multipart carriers

```
------boundary
Content-Disposition: form-data; name="role"
admin
------boundary
Content-Disposition: form-data; name="user[role]"
admin
------boundary
Content-Disposition: form-data; name="profile[role]"
admin
```

## GraphQL carriers

```graphql
mutation{ createUser(input:{username:"x",role:ADMIN}) }
mutation{ updateUser(id:9,input:{role:ADMIN}) }
mutation{ updateUser(id:9,input:{isAdmin:true,permissions:["*"]}) }
mutation{ updateProfile(input:{settings:{admin:true}}) }
mutation{ createOrder(input:{price:0,total:0}) }
```

## Method-override carriers

```
POST /users/me?_method=PUT    + body {role:admin}
POST /users/me?_method=PATCH  + body {role:admin}
POST /users/me                + X-HTTP-Method-Override: PUT
POST /users/me                + X-HTTP-Method-Override: PATCH
```

## The carrier-reach table

| Carrier | Reaches | When flat fails |
|---|---|---|
| flat JSON | merge-all, allowlist | — the baseline |
| nested JSON | deep-merge, association | flat allowlist |
| array | typed fields | scalar filtered |
| dup key | last-wins parser | filter-vs-binder gap |
| form flat | form binder | JSON schema |
| form prefixed | Rails/PHP nesting | flat key dead |
| dotted | qs/.NET | flat key dead |
| query | params union | body schema |
| multipart | third parser | JSON + form dead |
| GraphQL | args schema | REST dead |
| override | routing perm | method dead |
