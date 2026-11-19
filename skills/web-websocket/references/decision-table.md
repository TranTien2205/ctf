# Decision table — the observed reply → the verdict → the next step

## The handshake replies

| The reply | The verdict | The next step |
|---|---|---|
| `101` on foreign `Origin` | CSWSH-candidate | the binding + SameSite + data legs |
| `403` on foreign `Origin` | the check exists | the bypass set |
| `403` on ALL bypasses | `uniform` — `origin` closed | move on |
| `101`+cookie+data | the cookie binds | CSWSH-verify / probe the message-side |
| `101`+no-cookie+data | unauth channel | the data-action surface |
| `101`+no-cookie+drop-all | a closed channel | a `gap`, not a finding |
| `401`/`403` on no-credential | the upgrade is authed | the credential check |
| `?token=` on the URL | credential-in-URL | `web-auth-session` + record the channel cell |

## The message replies — the verdicts

| The reply | The verdict | The route |
|---|---|---|
| `{"id":"victim","data":...}` | a message-IDOR | `web-idor` |
| `{"flag":...}`/`{"admin":...}` | a dispatch gap | the flag directly |
| `{"results":[...]}` after `' OR 1=1` | SQLi | `web-sqli` |
| `49` after `{{7*7}}` | SSTI | `web-ssti` |
| `uid=0...` after `;id` | CMDi | `web-command-injection` |
| `root:x:...` after `../../` | LFI | `file-read-primitives` |
| the entity's data after `<!ENTITY>` | XXE | `web-xxe` |
| a server fetch reply after `url:` | SSRF | `web-ssrf` |
| `{"role":"admin"}` accepted | a self-grant | `web-mass-assignment` |
| a pushed feed after `subscribe <other>` | a subscription-IDOR | `web-idor` |
| a state-change after `{"action":"x"}` | a write-side gap | the state-read confirm |

## The negative replies — the dead ends

| The reply | The verdict | The next step |
|---|---|---|
| `{"error":"forbidden"}`/`"unauthorized"` | `uniform` — a real rejection | close the cell |
| `{"error":"not found"}`/`"invalid"` | a resource rejection | a KNOWN-other id re-probe |
| `{"error":"unknown action"}` | a weak-negative | the bundle's real action set |
| `{"error":"malformed"}`/`"bad request"` | a framing error | the correct envelope |
| silence/drop | a `gap` | a state-change check / a different field |
| `500`/crash | a `candidate` differential | the parser/branch probe |
| `pong`/`ok`/echo | `surface` | not a finding |

## The coverage decision

```
any cell oracle     -> the verbatim record + the route
all cells uniform   -> the socket is closed; the negative ledger
cells unmeasured    -> the budget decides which to spend on
```

## The decision-record

`decision: <cell>: <the reply-shape> -> <the verdict> -> <the next step>`
— each observed reply mapped to a verdict + a step.
