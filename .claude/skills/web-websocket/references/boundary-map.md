# Boundary map — each boundary, the checks that cross it

## The principal boundary — the user-to-user read/write

| The check | Crosses | The route |
|---|---|---|
| `{"action":"read","id":"<other>"}` | reads another's object | `web-idor` |
| `{"action":"open","doc":"<other>"}` | opens another's doc | `web-idor` |
| `{"action":"history","room":"<other>"}` | reads another's room | `web-idor` |
| `{"action":"conversation","id":"<other>"}` | another's conversation | `web-idor` |
| `{"action":"get","user_id":<n>}` | another's record | `web-idor` |
| `{"action":"view","account":"<other>"}` | another's account | `web-idor` |
| `{"action":"list","org":"<other>"}` | another's org | `web-idor` |
| `{"action":"balance","account":"<other>"}` | another's balance | `web-idor` |
| `{"action":"export","object":"<other>"}` | another's export | `web-idor` |
| `{"action":"fetch","item":"<other>"}` | another's item | `web-idor` |
| `SUBSCRIBE /user/<other>/queue` | another's queue | `web-idor` |
| `{"type":"subscribe",<other-query>}` | another's graphql field | `web-graphql` |
| `{"action":"update","id":"<other>",...}` | writes another's object | `web-idor`/`web-logic-flaw` |
| `{"action":"delete","id":"<other>"}` | deletes another's object | `web-idor`/`web-logic-flaw` |
| `{"action":"transfer","from":"<other>","to":"me"}` | moves another's asset | `web-logic-flaw` |

## The role boundary — the user-to-privileged

| The check | Crosses | The route |
|---|---|---|
| `{"action":"admin"/"debug"/"internal"/"system"}` | the admin handler | `web-auth-session`/`web-logic-flaw` |
| `{"action":"eval"/"exec"/"sql"/"flag"/"config"}` | an eval/exec/flag/config | `web-auth-session`/RCE |
| `{"action":"broadcast"/"announce"/"emit-all"}` | every socket | `web-logic-flaw` |
| `{"action":"set_role"/"impersonate"/"grant"/"reset"/"su"/"login_as"}` | a privilege-esc | `web-auth-session` |
| `{"action":"dump"/"export"/"backup"/"metrics"/"reload"/"migrate"/"seed"}` | a dump/export | `web-info-disclosure` |
| `{"action":"x","role":"admin"/"perm"/"is_admin"/"debug"/"internal"/"scope"/"level"/"sudo"}` | a self-grant | `web-mass-assignment` |
| `{"action":"x","user":{"role":"admin"}}` | a nested self-grant | `web-mass-assignment` |
| `{"action":"x","__proto__":{"role":"admin"}}` | a polluted grant | `web-prototype-pollution` |
| `42/admin`/`{"action":"admin:x"/"internal:x"/"system.x"/"debug/x"}` | a privileged namespace | `web-auth-session` |
| `{"type":"admin"/"internal"}`/`{"event":"admin"}`/`{"cmd":"admin"}` | a type/event/cmd-dispatch | `web-auth-session` |

## The identity boundary — the self-to-other

| The check | Crosses | The route |
|---|---|---|
| `{"from":"<other>","action":"x"}` | sends as another | `web-mass-assignment`/`web-auth-session` |
| `{"user_id":<n>,"action":"x"}` | acts as another | `web-mass-assignment` |
| `{"sender":"admin","action":"x"}` | sends as admin | `web-auth-session` |
| `{"user":{"id":"<other>","role":"<r>"},"action":"x"}` | a claimed principal | `web-auth-session` |
| `{"from":"<other>","action":"flag"}` | a flag-action as another | `web-auth-session` |
| `{"action":"dm","to":"<x>","from":"<other>"}` | a spoofed dm | `web-mass-assignment` |

## The sink boundary — the field-to-sink

| The check | Crosses | The route |
|---|---|---|
| `{"q":"<sqli>"}` | the field -> the datastore | `web-sqli` |
| `{"q":{"$ne":null}}/"id":{"$gt":""}` | the field -> the doc-query | `web-nosqli` |
| `{"name":"{{tpl}}"/"text":"${..}"` | the field -> the template | `web-ssti` |
| `{"file":"<path>"/"doc":"..\\"}` | the field -> the filesystem | `file-read-primitives` |
| `{"host":"<cmd>"/"cmd":"id"}` | the field -> the shell | `web-command-injection` |
| `{"xml":"<entity>"}` | the field -> the XML parser | `web-xxe` |
| `{"data":"<ser>"}` | the field -> the deserializer | `web-deserialization` |
| `{"url":"<fetch>"}` | the field -> the server fetch | `web-ssrf` |
| `{"obj":{"__proto__":{..}}}` | the field -> the prototype | `web-prototype-pollution` |
| `{"order":"<inject>"/"sort":"<inject>"}` | the field -> the sort/query | `web-sqli` |

## The channel boundary — the socket's scope

| The check | Crosses | The route |
|---|---|---|
| `{"action":"subscribe","channel":"internal"}` | the internal channel | `web-idor` |
| `{"action":"join","room":"secret"}` | the restricted room | `web-idor` |
| `{"action":"watch","doc":"admin-doc"}` | another's doc-feed | `web-idor` |
| `{"action":"listen","topic":"internal"}` | the internal feed | `web-idor` |
| `42/admin`/`42["internal",{...}]` | the privileged namespace | `web-auth-session` |
| `SUBSCRIBE {#,+,/internal,$SYS}` | the whole/internal topic-space | `web-idor` |
| `{"action":"broadcast"/"emit-all"}` | every connected socket | `web-logic-flaw` |
| `{"action":"subscribe","topic":"/user/<other>/*"}` | another's topic subtree | `web-idor` |

## The session boundary — the context's scope

| The check | Crosses | The route |
|---|---|---|
| `{"session_id":"<other>"}` | another's session | `web-websocket`/`web-auth-session` |
| `{"resume":"<old-session>"}` | the stale context | `web-websocket`/`web-auth-session` |
| `{"reconnect":true,"session_id":"<x>"}` | a resumption | `web-websocket`/`web-auth-session` |
| `{"seq":0}`/`{"offset":0}`/`{"lastEventId":-1}` | the backlog | `web-websocket`/`web-idor` |
| `{"action":"history","from":0,"to":N}` | the full history | `web-websocket`/`web-idor` |
| `?token=<stale>`/`?jwt=<forgeable>` | a stale/forgeable auth | `web-auth-session` |

## The boundary-verdict — the crossing

A boundary is crossed when the reply/state shows the OTHER side — the
other-object's data, the privileged action's reply, the sink's eval, the
internal feed, another's session — the verbatim bytes are the proof.

## The boundary-record

`boundary: <the check>: <the boundary>: <the verbatim crossing>` — each
crossing recorded; the boundary names what the check crossed.
