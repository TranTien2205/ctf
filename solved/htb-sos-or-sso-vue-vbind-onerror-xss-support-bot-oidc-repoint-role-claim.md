# SOS or SSO — SOLVED (self-solved)

- Platform: HackTheBox (web). Go + gin + gorm/sqlite backend, Vue 3 frontend,
  coreos/go-oidc, chromedp support bot.
- Date: 2026-09-23
- Target: `http://154.57.164.82:30358`
- Flag: redacted; read from note 1 in a live response
- Source was supplied.

## Where the flag lives, and why level is not enough

`PrepareDatabase` seeds it into a **private** note owned by the admin:

```go
CreateNote("My Secret", noteContent, true, &adminId)
```

and `noteAccessControl` checks private notes by identity, not by rank:

```go
if note.Private { return *note.AuthorID == userClaims.UserID }
```

So being *an* admin is useless. The chain has to end holding a session for
**that specific account**.

## 1. Stored XSS through Vue's dynamic component

`EditorView.vue` renders the note straight out of its base64 JSON:

```html
<component :is="item.type" v-bind="item.attr" ...>{{ noteContent[i].content }}</component>
```

Both `type` and `attr` are attacker-supplied. Vue 3's `shouldSetAsProp` contains

```js
if (nativeOnRE.test(key) && isString(value)) return false   // /^on[a-z]/
```

so an `on…` key whose value is a **string** is deliberately not set as a DOM
property — it falls through to `setAttribute`, and the browser then compiles it
as an inline handler. `{"type":"img","attr":{"src":"x","onerror":"…"}}` is
stored XSS, and `/api/note` accepts it with no session at all.

## 2. The reviewer bot hands over SUPPORT

`ReportNote` runs `util.VisitAndExamineNote`, which mints a token for
`support@wo.htb`, sets it as a cookie in chromedp and navigates to the note. The
handler therefore executes at `SUPPORT_LEVEL` — precisely what
`/api/support/faction/:id/config` requires. One `fetch` from inside the bot
repoints faction WO:

```js
fetch('/api/support/faction/1/config',{method:'POST',
  headers:{'X-NOTES-CSRF-PROTECTION':'1','Content-Type':'application/json'},
  body:JSON.stringify({clientId,clientSecret,endpoint:'<our IdP>'})})
```

The CSRF guard is a static header value, so scripted requests satisfy it
trivially.

## 3. The IdP decides the role

`RegisterUser` trusts the identity provider completely:

```go
if claims.Role == nil { roleName = "user" } else { roleName = *claims.Role }
role := database.FindRoleWithName(roleName)
```

`role` is a **userinfo claim**. Pointing the faction at an OIDC provider we run
means we choose it — `"admin"` exists in the seeded roles, so the first login
mints an ADMIN-level account, and `/api/admin/users` then discloses the real
admin's randomised address.

## 4. Logging in *as* the admin

`ProcessSSOCallback` looks the email up before it decides anything:

```go
user := database.FindUserWithEmail(*claims.Email)
if user == nil { user = RegisterUser(...) } else {
    if user.FactionID != uint64(ssoSession.FactionID) { return "", errors.New("wrong faction buddy") }
}
return GenerateToken(user, 1800)
```

A second login asserting the admin's address, through the faction that account
already belongs to, returns a token for **that** user — `id` and all. `GET
/api/note/1` then decodes to the flag.

The OIDC dance never needs a browser: `/auth/sso` hands back the authorization
URL *including* the `state` that keys `ssoSessions`, so the callback can be
called directly with that state and any `code`.

## Practical notes

- The IdP only has to satisfy four steps: serve a discovery document whose
  `issuer` matches the registered endpoint byte for byte, answer **POST**
  `/token` with an `id_token` signed by a key published at `jwks_uri`, and
  answer `/userinfo` with `email`, `username` and `role`. Static hosting is not
  enough because of the POST.
- The published `id_token` `aud` must equal the `clientId` stored in the config,
  since `ProcessSSOCallback` verifies with `oidc.Config{ClientID: …}`.
- ngrok is fine here even though a previous chain card warns against it: its
  interstitial targets browsers, and every consumer of this IdP is Go's HTTP
  client.

## Traps

- **Level is not identity.** Reaching ADMIN_LEVEL does not open a private note;
  the check is on the author's user id, which is what forces the second login.
- The seeded providers (`https://wo.htb/idp` and friends) do not resolve, so
  `GetRedirectUrlFromFaction` silently returns the raw endpoint with no `state`.
  That non-URL response is the cheapest confirmation that the provider is
  unreachable and that repointing is the whole game.
- The bot's banned-word list plus its fixed XPath click is the **Delete** button:
  putting "nuclear" in the note makes the bot remove the note after running the
  payload. Convenient for cleanup, but it means the note is gone on the next
  attempt.
- `CreateOIDCConfig` validates the endpoint before storing it, which makes the
  original `https://wo.htb/idp` value **unrestorable** through the API once
  changed — the domain does not resolve, so the write is rejected.

## Cleanup performed

The planted note was deleted by the bot itself. The account created through the
forged role claim was removed with `/api/admin/users/7/ban`, leaving the seeded
six users. The IdP and its tunnel were stopped, so `/auth/sso` for faction WO now
returns a bare endpoint with no session — the same inert state as the original
unreachable provider. The stored endpoint string still names the dead tunnel
rather than `wo.htb`, because the API refuses to store an endpoint it cannot
reach.

## Reusable lessons

- **`v-bind` of an attacker-controlled object is an XSS sink** even though Vue
  escapes interpolation: the framework explicitly routes string-valued `on…`
  keys to `setAttribute`.
- **A reviewer bot is a privilege, not just a viewer.** Read what account it
  authenticates as and what that account can reach before designing the payload.
- **Whoever runs the IdP decides the claims.** Any field the app copies out of
  userinfo — role, group, tenant — is attacker-controlled the moment the provider
  endpoint is writable.
- **"Find by email, then issue a token" is account takeover** whenever the email
  comes from an identity provider the attacker controls.
- **An authorization URL that contains the state is an invitation to skip the
  browser.** The callback only needs the state and any code.
