# Decision catalogue — the reply-shape decision tree, indexed

## The first-level split — the handshake

```text
the upgrade replies:
  101 Switching Protocols   -> the channel opened -> the binding/auth cells
  401/403 Forbidden         -> authed -> the credential cell
  400/426/Upgrade Required  -> the path/headers -> the framing
  301/302                   -> an HTTP auth first -> the login
  404                       -> the wrong path -> the bundle's real path
```

## The second-level split — the channel's first reply

```text
the 101-channel's first reply:
  a data frame              -> an unauth channel OR a bound channel
  an auth-demand            -> a first-frame token — probe the auth shape
  silence/drop-all          -> a closed channel / a subscribe-only — a gap
  a pong/ok/echo            -> surface — not a finding yet
```

## The third-level split — the message reply

```text
a mutated-field reply:
  another's object          -> oracle: IDOR
  a privileged action reply -> oracle: dispatch
  an eval/echo ("49")       -> oracle: inject -> the payload class
  a pushed feed             -> oracle: subscribe-IDOR
  a state-change            -> oracle: write-side (confirm with a read)
  forbidden/unauthorized    -> uniform — a real rejection
  unknown action/field      -> weak-negative — the schema was guessed
  not found                 -> weak-negative — a real other's id re-probe
  malformed/bad request     -> framing error — the correct envelope
  silence/drop              -> gap — a state-change check
  500/crash                 -> candidate — a parser/branch differential
  pong/ok/echo              -> surface — not a finding
```

## The fourth-level split — the route

```text
oracle: IDOR               -> web-idor
oracle: dispatch           -> the flag directly / web-auth-session
oracle: inject             -> the payload's class
oracle: subscribe-IDOR     -> web-idor
oracle: write-side         -> the state-read confirm -> the impact
oracle: self-grant/spoof   -> web-mass-assignment / web-auth-session
oracle: CSWSH              -> web-websocket (the four-leg chain)
oracle: unauth             -> web-websocket / web-info-disclosure
oracle: token-URL          -> web-auth-session / web-info-disclosure
```

## The coverage decision

```text
any oracle      -> the verbatim record + the route + the chain
all uniform     -> the negative ledger; the escalation rungs
cells unmeasured -> the budget decides the order
any weak-neg    -> the re-probe before closing
any gap         -> a state-change/different-field check
```

## The escalate decision

```text
the socket is fully uniform AND the budget is spent ->
  decide.py answers escalate:
    chain_match -> a solved-shape card
    reclassify  -> the wrong class
    writeup_search -> the challenge+event writeup
    novel_plan  -> a bounded source-first plan
    fanout_sweep -> a parallel-layer close
    solver_handoff -> the solver
  -> NEVER a sixth variant of the same cell
```

## The decision-record

`decision: <the reply> -> <the verdict> -> <the step>` — each reply
shape mapped to a verdict + the next step.
