# Whitebox hunt — finding the OAuth surface in source

When source is available, the OAuth surface is readable: the `authorize` URL
construction, the `callback` handler's `state` check, the `redirect_uri`
validation, the cookie-setting code, the account-linking logic.

## The search patterns

```bash
# the authorize URL construction — where is redirect_uri built?
grep -rn "redirect_uri\|authorize\|response_type\|state=" --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.go" --include="*.rb" --include="*.php" src/

# the callback handler — where is state validated?
grep -rn "state\|callback\|oauth.*callback\|code=" --include="*.py" --include="*.js" --include="*.ts" src/

# the cookie setting — where is the token cookie set?
grep -rn "Set-Cookie\|cookie\|session\|token" --include="*.py" --include="*.js" --include="*.ts" src/

# the account linking — where is the OAuth identity mapped to a local account?
grep -rn "email\|username\|sub\|preferred_username\|userinfo" --include="*.py" --include="*.js" --include="*.ts" src/
```

## The `redirect_uri` construction

```python
# the pattern — redirect_uri is built from user input or a template
redirect_uri = request.args.get('redirect_uri', 'https://app/callback')
# or: redirect_uri = f"https://app/callback?return_to={request.args.get('return_to')}"
# or: redirect_uri = request.host_url + 'callback'
```

The check: is `redirect_uri` validated against a stored allowlist, or is it
built from a template that can be influenced?

## The `state` validation

```python
# the pattern — state is stored in the session before the redirect
session['oauth_state'] = secrets.token_urlsafe(32)
authorize_url = f"https://idp/authorize?...&state={session['oauth_state']}"

# the callback handler — does it check state == session['oauth_state']?
if request.args.get('state') != session.get('oauth_state'):
    abort(400, 'state mismatch')
```

The check: is `state` stored in the session, and is the callback handler
checking it? A missing check or a check against the wrong session is the bug.

## The `code` exchange

```python
# the pattern — the token request re-validates redirect_uri
token_response = requests.post('https://idp/token', data={
    'grant_type': 'authorization_code',
    'code': request.args.get('code'),
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': request.args.get('redirect_uri')  # re-validated?
})
```

The check: is `redirect_uri` on the token request re-validated against the
authorize step's `redirect_uri`?

## The cookie setting

```python
# the pattern — the token cookie is set with SameSite
response.set_cookie('token', token, httponly=True, secure=True, samesite='Lax')
# or: response.set_cookie('token', token, httponly=True)  # SameSite missing
# or: response.set_cookie('token', token, httponly=True, samesite='None', secure=True)
```

The check: is `SameSite` set on the token cookie? `Lax` or `Strict` closes
the cross-site write; missing or `None` leaves it open.

## The account linking

```python
# the pattern — the OAuth identity is mapped to a local account
user = User.query.filter_by(email=profile['email']).first()
if not user:
    user = User(email=profile['email'], oauth_sub=profile['sub'])
    db.session.add(user)
    db.session.commit()
```

The check: is the linking on `email` or `sub`? Is `email_verified` checked?
Is the linking automatic or does it require an authenticated step?

## The `loginSSO` bug

```python
# the pattern — the loginSSO step ignores credentials and uses the jar's token
def loginSSO():
    token = request.cookies.get('token')  # the jar's token, not the credentials
    if not token:
        abort(401)
    # the token is used directly — no credential check
    session['user'] = get_user_from_token(token)
```

The check: does the `loginSSO` step read the jar's token cookie and ignore
the credentials in the request body? This is the parameter-confusion bug.

## The registration race

```python
# the pattern — the registration endpoint is not idempotent
@app.route('/api/register', methods=['POST'])
def register():
    email = request.json['email']
    password = request.json['password']
    user = User(email=email, password=hash(password))
    db.session.add(user)
    db.session.commit()  # no uniqueness check — or a race on the check
```

The check: is there a uniqueness constraint on `email`? Is the check
atomic — a `SELECT` then `INSERT` is a race; a `UNIQUE` constraint is not.

## The `ShouldBindJSON` bug

```go
// the pattern — Gin's ShouldBindJSON reads the raw body as JSON
// regardless of Content-Type
func login(c *gin.Context) {
    var req LoginRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.AbortWithStatus(400)
        return
    }
    // req is parsed from the raw body — Content-Type is ignored
}
```

The check: does the binder parse the raw body as JSON regardless of
`Content-Type`? A `text/plain` or `application/x-www-form-urlencoded` body
with JSON content is parsed.
