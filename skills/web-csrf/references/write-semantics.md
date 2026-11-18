# Write semantics — what each endpoint type's CSRF actually does

The write's effect decides the chain. Each endpoint type's CSRF
outcome and the readback that proves it.

---

## 1. Email/attribute change → account takeover

```text
the write: POST /change-email — swaps the victim's email to yours
the chain: password-reset to your email → reset → log in → takeover
the readback: the victim's account now has YOUR email (check via
  the reset flow or a profile read)
```

```html
<form action="/change-email" method=POST>
<input name=email value="attacker@evil.com"></form>
```

## 2. Password/credential change → direct takeover

```text
the write: POST /change-password — sets a new password you know
the chain: log in with the new password → the account
the readback: log in as the victim with your password → success
```

## 3. Role/privilege grant → escalation

```text
the write: POST /admin/role or /grant — gives the attacker admin
the chain: your account is now admin → the admin surface opens
the readback: your account's role=admin → the admin endpoints answer
```

## 4. Asset transfer → exfil

```text
the write: POST /transfer — moves an asset to you
the chain: the asset/flag lands on your account
the readback: your balance/objects include the transferred asset
```

## 5. Config/setting write → the foothold

```text
the write: POST /settings — flips a config the next layer reads
the chain: a debug-mode on, a private→public toggle, a webhook URL
the readback: the config's effect — a public object, a debug page
```

## 6. Object create → the planted-content

```text
the write: POST /post /comment /note — creates content
the chain: a stored-XSS payload, a marker, a visible record
the readback: the object appears — the stored content renders
```

## 7. Delete → the destructive write (handle carefully)

```text
the write: DELETE /x or GET /delete — removes an object
the chain: rarely useful alone — a nuisance, a DoS, or a cover-up
the readback: the object 404s
WARNING: a destructive write on a shared instance — blast_radius.
  test on an object you created, never a victim's data.
```

## 8. Login/credential-plant → session swap (login-CSRF)

```text
the write: POST /login — sets the victim's session to your account
the chain: the victim's actions land on your account (SSOS)
the readback: YOUR account has the victim's deposit/flag
```

## 9. State-transition → approve/confirm

```text
the write: POST /approve /confirm /verify — flips a pending state
the chain: an approved request, a confirmed action
the readback: the pending→approved state change
```

## 10. Message/send → the exfil-via-message

```text
the write: POST /message — sends a message (with the flag?) to you
the chain: the victim's context writes the flag into a message to
  the attacker's account
the readback: the message on your account
```

## 11. Upload → the file-write

```text
the write: POST /upload (multipart) — delivers a file
the chain: a stored file that renders/executes
the readback: the uploaded file is reachable/executable
```

## 12. Flag-submit → the challenge-write

```text
the write: POST /submit /answer — the bot submits the flag for you
the chain: the bot's privileged context submits the flag to your
  account (the SSOS shape)
the readback: the flag/answer recorded on your account
```

## 13. Share/permission → the access-grant

```text
the write: POST /share /invite — grants you access to the victim's
  object
the chain: a private object shared to you → you read it
the readback: the shared object accessible from your account
```

## 14. Webhook/callback URL → the planted-SSRF

```text
the write: POST /webhook /callback — sets a URL the server fetches
the chain: the server's later fetch is an SSRF to your listener or
  an internal target
the readback: the OOB hit or the internal action
```

## 15. The write→readback matrix

| Write | The readback oracle |
|---|---|
| email-change | the reset flow or profile read shows your email |
| password-change | log in with the new password |
| role-grant | your account is admin |
| transfer | your balance/objects include the asset |
| config | the config's effect visible |
| create | the object present in a list |
| delete | the object 404s |
| login-plant | your account holds the victim's deposit |
| approve | the state is approved |
| message | the message on your account |
| upload | the file reachable |
| flag-submit | the flag on your account |
| share | the object accessible to you |
| webhook | the OOB hit |

## 16. The "which write is worth it" — the flag-proximity rank

```text
the write's value = how directly it reaches the flag:
1. a write that moves the flag to a readable place → direct
2. a write that grants the privilege to read it → one step
3. a credential-plant → the victim's flag-path actions land on you
4. a config-write → unlocks the next layer
5. a stored-XSS plant → the next viewer's session
```
