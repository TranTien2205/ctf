# Evidence map — each finding → the verbatim proof → the gate args

## The evidence-shape map

| Finding | The verbatim proof | The gate args |
|---|---|---|
| CSWSH | leg1 `Origin:evil -> 101` + leg2 `Cookie:session -> {"user":"victim"}` + leg3 `Set-Cookie: SameSite=Lax` + leg4 `{"action":"me"} -> victim-data` | `--class web-websocket` + `--evidence-kind impact` |
| unauth | no-credential `101` + `{"action":"dump"} -> {"users":[...]}` | `--class web-websocket` + `--evidence-kind class` |
| message-IDOR | `{"action":"read","id":"<other>"} -> {"id":"<other>",...}` | `--class web-websocket` + `--evidence-kind class` |
| membership-IDOR | `{"action":"join","room":"<x>"} -> the pushed feed` | `--class web-websocket` + `--evidence-kind class` |
| action-dispatch | `{"action":"admin"} -> {"flag":...}/{"admin":...}` | `--class web-websocket` + `--evidence-kind class` |
| self-grant | `{"action":"x","role":"admin"} -> the grant accepted` | `--class web-websocket` + `--evidence-kind class` |
| spoof | `{"from":"<other>","action":"x"} -> acts-as-other` | `--class web-websocket` + `--evidence-kind class` |
| injection | `{"<sink-field>":"<payload>"} -> the eval/read` | `--class web-websocket` + the payload class + `--evidence-kind class` |
| write-side | `{"action":"transfer",...} -> a state-change (a second read)` | `--class web-websocket` + `--evidence-kind impact` |
| subscription-IDOR | `{"action":"subscribe","channel":"<other>"} -> the pushed feed` | `--class web-websocket` + `--evidence-kind class` |
| token-in-URL | `wss://x/ws?token=<jwt>` — the verbatim URI | `--class web-auth-session`/`web-info-disclosure` + `--evidence-kind class` |
| resumption | `{"session_id":"<old>"} -> the resumed foreign context` | `--class web-websocket` + `--evidence-kind class` |
| graphql-WS | `{"type":"subscribe",<query>} -> the pushed data` | `--class web-websocket`/`web-graphql` + `--evidence-kind class` |
| binary-field | a binary frame -> `proto_decode` -> `field N` = the flag | `--class web-websocket` + `--evidence-kind impact` |

## The verbatim-rule map

| The evidence IS | The evidence is NOT |
|---|---|
| the bytes the server sent | a paraphrase of the reply |
| `{"id":"<other>","data":...}` | "it returned another's data" |
| `{"flag":"..."}` | "the flag was there" |
| `49` | "the template evaluated" |
| a `forbidden`/`403`/`401`/`1008` | "it was blocked" |
| a `SameSite=Lax` header | "the cookie travels" |

## The substring-check map

`hooks.py post-probe --verdict confirms` asserts `--evidence` ⊂ `--response`:

```text
--response:  the raw frame bytes the server sent — the whole reply
--evidence:  the verbatim excerpt — the {"id":"<other>",...} / {"flag":...} /
             49 / the pushed feed — a substring of --response
```

A paraphrase fails the substring check — the evidence is the bytes.

## The evidence-kind map

| The evidence shows | The kind |
|---|---|
| the class is present — a mechanism is confirmed | `class` |
| the impact is produced — a boundary crossed / a state changed / a flag read | `impact` |

## The record map

```
evidence: <the finding>: <the verbatim proof>: <the kind>: <the route>
  --class web-websocket
  --evidence-kind <class|impact>
  --evidence "<the verbatim bytes>"
  --response "<the raw frame bytes>"
```

Each finding carries the verbatim reply + the kind + the route — the
bytes are the proof.
