# Wordlists — secrets, ids, endpoint seeds

Feed `session_dissect.py --try-keys --wordlist` for JWT/HMAC secrets;
feed `id_sweep` for ids; grep bundles for endpoint names.

---

## 1. JWT / HMAC secrets — the high-yield set

Ordered by CTF hit-rate. Point `session_dissect --wordlist` at a file of
one-per-line secrets:

```
secret
secret123
secretkey
secret_key
SECRET
jwt_secret
JWT_SECRET
jwt-secret
your-256-bit-secret
your_jwt_secret
your-jwt-secret
your-256-bit-secret-key
supersecret
super_secret
super-secret
supersecretkey
sup3rs3cr3t
changeme
change_me
change-me
password
password123
admin
admin123
administrator
key
mykey
my_key
my-secret
my_secret
my-secret-key
my_secret_key
privatekey
private_key
private-key
signingkey
signing_key
signing-key
hs256
HS256
hmacsecret
hmac_secret
token
token123
token_secret
token-secret
auth
auth123
auth_secret
auth-secret
session
session_secret
session-secret
sessionkey
session_key
test
testing
dev
development
debug
local
localhost
staging
production
123456
12345678
123456789
1234567890
qwerty
qwerty123
letmein
let_me_in
welcome
welcome1
welcome123
abc123
abcdef
flask-secret
flask_secret
django-secret
django_secret
django-insecure
django-insecure-key
django-insecure-secret
rails-secret
rails_secret
express-secret
express_secret
laravel-secret
laravel_secret
app_key
APP_KEY
app-key
appkey
app_secret
APP_SECRET
keyboard-cat
keyboard_cat
shhhhh
shhh
s3cr3t
s3cr3t!
S3cr3t
p@ssw0rd
p4ssw0rd
iloveyou
monkey
dragon
master
sunshine
princess
football
baseball
shadow
michael
jennifer
hunter
trustno1
ranger
charlie
thomas
ginger
michelle
jordan
buster
pepper
harley
banana
apple
orange
grape
kiwi
mango
lemon
cherry
strawberry
blueberry
raspberry
blackberry
cranberry
coconut
pineapple
watermelon
cantaloupe
honeydew
papaya
guava
lychee
passionfruit
dragonfruit
starfruit
persimmon
pomegranate
apricot
peach
plum
nectarine
fig
date
olive
avocado
tomato
cucumber
pepper
carrot
potato
onion
garlic
ginger
spinach
lettuce
kale
cabbage
broccoli
cauliflower
asparagus
artichoke
eggplant
zucchini
squash
pumpkin
turnip
radish
beet
celery
leek
shallot
chive
parsley
cilantro
basil
oregano
thyme
rosemary
sage
mint
dill
tarragon
bay
coriander
cumin
turmeric
paprika
saffron
cardamom
cinnamon
nutmeg
clove
allspice
vanilla
chocolate
coffee
tea
cocoa
sugar
salt
honey
maple
syrup
molasses
agave
stevia
butter
cream
milk
cheese
yogurt
bread
rice
pasta
noodle
pizza
burger
sandwich
taco
burrito
sushi
ramen
dumpling
spring-roll
tempura
teriyaki
wasabi
soy-sauce
miso
tofu
seaweed
kimchi
pickle
relish
mustard
ketchup
mayo
vinegar
oil
jwt
jwt123
jwttoken
jwtsecret
jwt-secret
jwt_secret
jsonwebtoken
json-web-token
jws
jwe
jwk
jwks
unguessable
notsecret
fake_secret
temp_secret
hard-to-guess
hard!to-guess
very_secret
verysecret
really-secret
the-secret
thisissecret
this_is_secret
this-is-secret
no-secret
nosecret
empty
blank
none
null
undefined
x
xx
xxx
xxxx
a
aa
aaa
aaaa
0
00
000
0000
1
11
111
1111
pass
passwd
pwd
pass123
passwd123
pwd123
passw0rd
p@ssword
secret0
secret1
secret2
secret3
secret4
secret5
secret6
secret7
secret8
secret9
key0
key1
key2
key3
key4
key5
key6
key7
key8
key9
app0
app1
app2
app3
```

App-specific: prepend/append the app name, the challenge name, the
domain: `<name>`, `<name>123`, `<name>-secret`, `<name>_secret`,
`<name>-key`, `<name>_key`, `secret-<name>`, `key-<name>`.

## 2. Session-id seeds — common predictable patterns

```
admin, administrator, root, system, user, test, guest, demo, debug,
dev, staging, prod, production, local, localhost, default, backup,
temp, tmp, old, new, api, service, bot, crawler, worker, cron,
session, sid, token, auth, jwt, oauth, sso, saml, openid, bearer
```

## 3. Endpoint name seeds — auth surface

```
/login,/logout,/signin,/signout,/signup,/register,/registration
/auth,/authn,/authz,/authenticate,/authorize,/authentication
/oauth,/oauth2,/oauth/callback,/oauth/authorize,/oauth/token
/sso,/sso/login,/sso/callback,/sso/authorize,/saml,/saml2
/session,/sessions,/session/new,/session/create,/session/destroy
/token,/tokens,/token/new,/token/create,/token/refresh,/token/revoke
/refresh,/revoke,/invalidate,/expire,/expire_session
/refresh_token,/access_token,/id_token
/me,/self,/whoami,/profile,/account,/user,/users,/users/me
/admin,/admin/users,/admin/sessions,/admin/tokens,/admin/flag
/password,/password/reset,/password/forgot,/password/change
/forgot,/forgot-password,/forgot_password,/reset,/reset-password,/reset_password
/change-password,/change_password,/update-password
/verify,/verify-email,/verify_email,/confirm,/confirm-email
/activate,/activate-account,/activation
/mfa,/mfa/verify,/mfa/setup,/mfa/enable,/mfa/disable
/totp,/totp/verify,/2fa,/otp,/otp/verify
/backup-codes,/recovery-codes,/mfa/backup
/invite,/invites,/invite/accept,/join
/impersonate,/switch-user,/sudo,/su,/become
/api,/api/v1,/api/v2,/api/me,/api/auth,/api/session,/api/token
/graphql,/graphiql,/playground
/debug,/debug/session,/debug/sessions,/debug/users
/health,/healthz,/status,/info,/version
/.well-known/jwks.json,/jwks.json,/oauth/jwks,/oauth/.well-known
/openid-configuration,/.well-known/openid-configuration
/phpinfo.php,/info.php,/server-status
/logs,/log,/debug/logs,/admin/logs
```

## 4. Claim-name seeds — the privileged field to forge

```
role, roles, admin, isAdmin, is_admin, isStaff, is_staff,
isSuperuser, is_superuser, superuser, staff, sudo, su, root, system,
verified, email_verified, active, enabled, approved, confirmed,
balance, credits, score, level, tier, plan,
permissions, perms, scope, scopes, groups, privileges, capabilities,
id, uid, user_id, userId, sub, subject, account_id, accountId,
tenant_id, tenantId, org_id, orgId, owner_id, ownerId, createdBy,
iat, nbf, exp, iss, aud, jti, typ, alg, kid, jku, x5u, x5c, cty
```

## 5. Cookie-name seeds

```
session, sid, sessionid, session_id, PHPSESSID, JSESSIONID,
connect.sid, laravel_session, rack.session, express.sid, django_session,
auth, auth_token, token, jwt, access_token, refresh_token, id_token,
remember_me, remember_token, remember, persistent, device_id, device,
mfa_remember, trust_device, trusted_device, logged_in, authenticated,
user, uid, user_id, username, role, admin, is_admin, isAdmin
```
