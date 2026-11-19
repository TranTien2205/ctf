# Quick map — the one-line check → the verdict → the route

## The handshake quick-map

```text
origin:evil -> 101          -> CSWSH-candidate -> cswsh.md
origin:evil -> 403          -> the bypass set  -> evasion-deep.md
cookie:x -> {"user":"victim"} -> cookie-binding -> cswsh.md
?token=eyJ -> 101            -> credential-in-URL -> web-auth-session
no-auth -> 101+data         -> unauth channel -> handshake-side-deep.md
no-auth -> 101+drop         -> a closed channel -> edge-cases-deep.md
subproto:graphql-ws -> 101  -> a graphql surface -> per-transport-deep.md
SameSite=Strict             -> the browser defense -> cswsh.md
```

## The message quick-map

```text
{"action":"read","id":"<other>"} -> the object     -> web-idor
{"action":"join","room":"<x>"}   -> the feed        -> web-idor
{"action":"subscribe","<other>"} -> the feed        -> web-idor
{"action":"admin"}               -> a privileged   -> the flag/web-auth-session
{"action":"flag"}                -> the flag        -> the flag
{"action":"eval","code":"x"}     -> an eval         -> RCE
{"action":"x","role":"admin"}    -> a self-grant    -> web-mass-assignment
{"from":"<other>"}               -> a spoof         -> web-mass-assignment
{"q":"' OR 1=1"}                 -> sqli            -> web-sqli
{"name":"{{7*7}}"}               -> ssti            -> web-ssti
{"file":"../../x"}               -> lfi             -> file-read-primitives
{"host":"x;id"}                  -> cmdi            -> web-command-injection
{"xml":"<!ENTITY.."}             -> xxe             -> web-xxe
{"url":"http://.."}              -> ssrf            -> web-ssrf
{"data":"<ser>"}                 -> deser           -> web-deserialization
{"obj":{"__proto__":{..}}}       -> pollution       -> web-prototype-pollution
{"action":"broadcast"}           -> a write-blast   -> the state-read
{"action":"transfer"}            -> a write-side    -> the state-read
{"session_id":"<old>"}           -> a resumption    -> web-websocket
{"seq":-1}/{"lastEventId":-1}    -> a backlog       -> web-websocket
SUBSCRIBE /user/<other>          -> a queue-IDOR    -> web-idor
SUBSCRIBE #                      -> a wildcard      -> web-idor
{"type":"subscribe",<query>}     -> graphql-over-WS -> web-graphql
42["<event>",{...}]              -> socket.io event -> the event class
```

## The negative quick-map

```text
"forbidden"/"unauthorized"       -> uniform — closed
"unknown action"/"invalid field" -> weak-neg — re-probe the schema
"not found" on a guessed id      -> weak-neg — a known-other id
"malformed"/"bad request"        -> framing-error — the real envelope
silence/drop                     -> gap — a state check
500/crash                        -> candidate — a differential
pong/ok/echo                     -> surface — not a finding
```

## The verdict-map — the reply → the class

```text
another's object     -> message-IDOR -> web-idor
a privileged reply   -> dispatch -> the flag
49/the-eval          -> inject -> the payload class
a pushed feed        -> subscribe-IDOR -> web-idor
a self-grant         -> the grant -> web-mass-assignment
acts-as-other        -> spoof -> web-auth-session
a state-change       -> write-side -> the impact
the victim's data    -> CSWSH -> web-websocket
```

## The map-discipline

The quick-map is the one-line cheat — the deep files carry the full
check-path; the map is the index, not the reference.
