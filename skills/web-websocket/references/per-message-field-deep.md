# Per message-field (deep) — every field, its gap, its probe

## The identity fields — the spoof surface

| Field | Probe | A gap replies |
|---|---|---|
| `from`/`sender` | `from:"victim"` | the frame acts as victim |
| `user_id`/`uid`/`user` | `user_id:2`/`"admin"` | another's context |
| `role`/`perm`/`is_admin`/`debug`/`internal`/`scope`/`level` | `role:"admin"` | a self-grant |
| `user`/`principal`/`subject` | `user":{"role":"admin"}` | a nested grant |

## The object fields — the IDOR surface

| Field | Probe | A gap replies |
|---|---|---|
| `id`/`doc`/`object`/`item`/`record` | `id:"victim"` | another's object |
| `room`/`channel`/`conversation`/`thread` | `room:"admin"` | the restricted feed |
| `topic`/`subscription`/`feed` | `topic:"internal"` | the internal feed |
| `account`/`org`/`tenant`/`project` | `org:"acme"` | another's tenant |
| `user_id`/`owner`/`target` | `user_id:2` | another's record |
| `to`/`recipient`/`target` | `to:"admin"` | a write to another |
| `message`/`note`/`ticket`/`order`/`file` | `id:"<other>"` | another's object |

## The dispatch fields — the action surface

| Field | Probe | A gap replies |
|---|---|---|
| `action`/`type`/`event`/`cmd`/`command`/`method`/`op`/`verb`/`kind`/`do`/`fn` | `action:"admin"` | a privileged reply |
| `action`/`event` + namespace | `admin:flag`/`system.exec` | a namespaced action |
| `handler`/`route`/`call`/`name` | `handler:"internal"` | an internal handler |

## The query/data fields — the injection surface

| Field | Probe | A gap replies |
|---|---|---|
| `q`/`search`/`query`/`filter`/`where` | `q:"' OR 1=1"`/`{"$ne":null}` | injected rows |
| `name`/`text`/`tpl`/`msg`/`input`/`value` | `name:"{{7*7}}"` | `49` evaluated |
| `file`/`path`/`filename`/`doc`/`name` | `file:"../../etc/passwd"` | the file |
| `host`/`cmd`/`exec`/`command`/`target` | `host:"x;id"` | the output |
| `url`/`fetch`/`webhook`/`callback`/`image` | `url":"http://..."` | a server fetch |
| `xml`/`data`/`import`/`parse`/`svg` | `<!ENTITY>`/`serialize` | the eval/read |
| `obj`/`config`/`set`/`merge`/`key`/`value` | `__proto__.x`/`{"$set"}` | a polluted/bound obj |
| `order`/`sort`/`field`/`column` | `order":"name,(case...)"` | an injected sort |

## The session/resume fields

| Field | Probe | A gap replies |
|---|---|---|
| `token`/`auth`/`jwt`/`session`/`key` | `token:"eyJ"`/`token:null` | an auth-override |
| `session_id`/`resume`/`seq`/`offset`/`lastEventId` | `seq:0`/`lastEventId:-1` | a history read |
| `reconnect`/`resume`/`context` | `resume:"<old-session>"` | a resumption gap |

## The field-probe discipline

- ONE field per frame — never two
- the CONTROL first — the known-good frame shape, verbatim
- the MUTATION — one field changed
- the VERDICT — the reply vs the control
- the RECORD — `field:<name>:<probe>:<verdict>`

## The field-inventory — the bundle names them

```bash
grep -riE '"(id|user_id|room|channel|action|type|event|role|from|to|
token|q|filter|file|path|url|data|obj|order|sort|seq|offset|session)":' /tmp/bundle
```

The bundle's field names are the REAL set — a guessed field is a weak
probe.
