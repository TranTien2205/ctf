# SSO and federated enumeration — the identity-provider leaks

## The account-exists oracle in the SSO flow

A `Sign in with Google/Microsoft/Okta` flow that returns
`account_not_found` on an unlinked email — a federated existence-oracle:

```bash
# the flow's identifier step
curl -s -X POST -d "login_hint=$KNOWN@corp.com" "$BASE/oauth/authorize"
curl -s -X POST -d "login_hint=$FAKE@corp.com"  "$BASE/oauth/authorize"
# -> a redirect to the IdP (account exists) vs an error (no account)
```

The `login_hint`/`identifier`/`email` step that redirects to the IdP
for a real account vs an error/`account_not_found` for a fake — the
existence leaks at the federation boundary.

## The SAML directory leak

A `user@external.com` vs `user@local.com` redirect — the app looks up
the email's domain to route to the IdP vs the local login:

```bash
curl -s -D - -o /dev/null -X POST -d "email=$KNOWN@corp.com" "$BASE/sso/login"
curl -s -D - -o /dev/null -X POST -d "email=$FAKE@corp.com"  "$BASE/sso/login"
# -> Location: https://idp.corp.com/... (a federated account)
#    vs Location: /local-login (a local account)
#    vs an error (no account at all)
```

Three outcomes — federated (redirect to IdP), local (redirect to local),
nonexistent (error) — a two-bit oracle: existence + account-type.

## The pre-hijack chain — `web-oauth-sso`

A confirmed unlinked-victim email that an SSO provider auto-links on
email match → register the victim's email yourself, or link your IdP
identity → log into the victim's account. `web-oauth-sso` owns the
exploit; `web-user-enum` confirms the email exists.

## The `invalid_grant` vs `invalid_client` oracle

```bash
curl -s -X POST -d "grant_type=password&username=$KNOWN&password=x&client_id=x" "$BASE/oauth/token"
curl -s -X POST -d "grant_type=password&username=$FAKE&password=x&client_id=x"  "$BASE/oauth/token"
```

RFC 6749: `invalid_grant` for a bad password. An app may return
`invalid_client`/`invalid_request`/a typed `error_description` for a
bad USER — the distinction leaks `exists`. Or a `error_description` that
names the account (`"user admin disabled"`).

## The passwordless/magic-link oracle

`POST /send-magic-link` — `"we emailed you a link"` vs `"no account"`,
or the send-side (the email only for a real row) — the reset/send
oracle in the passwordless form.

## The IdP-side oracle

A third-party IdP (Google/Microsoft/Okta) whose own login page
distinguishes `account not found` from `wrong password` — the
enumeration is the IdP's, but it leaks whether the target email is
registered THERE. A `Sign in with Google` that reveals the Google
account's existence — a federated leak.

## The federated boundary

- `web-user-enum` — the existence oracle at the federation boundary
- `web-oauth-sso` — the redirect/state/token/pre-hijack exploit
- `web-auth-session` — the session/token after the SSO

The enum confirms `exists`/`account-type`; the SSO class exploits the
flow. Record the oracle; route the exploit.
