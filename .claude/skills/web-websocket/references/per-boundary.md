# Per boundary — each boundary, the check that crosses it

## The principal boundary — the user-to-user

| The check | Crosses |
|---|---|
| `{"action":"read","id":"<other>"}` | reads another's object |
| `{"action":"open","doc":"<other>"}` | opens another's doc |
| `{"action":"history","room":"<other>"}` | reads another's room |
| `{"action":"subscribe","user_id":"<other>"}` | reads another's feed |
| `{"action":"balance","account":"<other>"}` | reads another's account |
| `{"action":"update","id":"<other>"}` | writes another's object |
| `{"action":"transfer","from":"<other>"}` | moves another's asset |
| `SUBSCRIBE /user/<other>/queue` | reads another's queue |
| `{"type":"subscribe","query":"user(id:<other>)"}` | another's graphql field |

## The role boundary — the user-to-privileged

| The check | Crosses |
|---|---|
| `{"action":"admin"}`/`"debug"`/`"internal"`/`"system"` | the admin handler |
| `{"action":"x","role":"admin"}`/`"perm"`/`"is_admin"`/`"scope"` | a self-grant |
| `{"action":"config"}`/`"set"`/`"reset"`/`"grant"`/`"impersonate"` | a privileged write |
| `{"action":"eval"/"exec"/"sql"/"flag"}` | an eval/exec/flag handler |
| `42/admin`/`42["internal",{...}]`/`{"action":"admin:x"}` | a namespaced admin |

## The identity boundary — the self-to-other

| The check | Crosses |
|---|---|
| `{"from":"<other>",...}` | sends as another |
| `{"user_id":"<other>",...}` | acts as another |
| `{"sender":"<other>",...}` | sends as another |
| `{"user":{"id":"<other>","role":"<r>"}}` | claims another's principal |
| `{"from":"<other>","action":"flag"}` | a flag-action as another |

## The sink boundary — the field-to-sink

| The check | Crosses |
|---|---|
| `{"q":"<sqli>"}` | the field → the datastore query |
| `{"name":"{{tpl}}"} | the field → the template engine |
| `{"file":"<path>"}` | the field → the filesystem |
| `{"host":"<cmd>"}` | the field → the shell |
| `{"xml":"<entity>"}` | the field → the XML parser |
| `{"data":"<ser>"}` | the field → the deserializer |
| `{"url":"<fetch>"}` | the field → the server-side fetch |
| `{"obj":{"__proto__":{...}}}` | the field → the prototype chain |

## The channel boundary — the socket's scope

| The check | Crosses |
|---|---|
| `{"action":"subscribe","channel":"internal"}` | the internal channel |
| `{"action":"join","room":"secret"}` | the restricted room |
| `42/admin`/`{"action":"admin:x"}` | the privileged namespace |
| `SUBSCRIBE {#,+,/internal}` | the whole/internal topic-space |
| `{"action":"broadcast"}`/`"emit-all"` | every connected socket |

## The boundary-verdict

A boundary is crossed when the reply/state shows the OTHER side — the
other-object's data, the privileged action's reply, the sink's eval, the
internal feed — the verbatim bytes.
