# Workflow map — the pass as a flowchart

```
[scope + known-good + form inventory]
        |
        v
[direct oracle: check-username / register-taken] ----yes--> [the class
        |no                                                 confirmed ->
        v                                                   bounded list]
[per-form 3-request pair]
        |
        v
[per-channel: body -> status -> side -> timing]
        |
        +-- a channel differs + repeats + tracks-username --> [oracle
        |                                                    confirmed]
        +-- all uniform on this form -----------------------> [form closed]
        |
        v
[throttle: bounded burst -> absent/threshold/lock]
        |
        +-- limited -> [bypass: XFF/session/endpoint/method]
        |
        v
[bounded candidate list -> the verified names]
        |
        v
[route each name -> web-auth-session/idor/logic/oauth]
        |
        v
[record: per-cell oracles, throttle, names, negatives]
```

## The branch rules

- a direct-oracle hit **short-circuits** — the class is confirmed; go
  to the bounded list
- a form's all-uniform is a **cell-closure**, not a class-closure — the
  next form stays open
- a throttle that is **bypassed** reopens the unbounded loop — record
  the bypass as the finding
- a confirmed name is the **enum's output** — the chain moves to the
  neighbor class, not a re-probe

## The bounded rule

The map runs once per target — each node is a bounded measurement, not
a retry loop. A measured-uniform node is never re-probed; the map moves
forward or closes.
