# Per channel — each channel type, the cells it carries

## The `me`/`profile`/`account` channel

```text
the frames:   {"action":"me"} / {"action":"profile"} / {"action":"account"}
the fields:   user_id / account / id
the cells:    a self-read baseline + a {"user_id":"<other>"} IDOR +
              a role/perm field
the flag:     the other-account's private field
```

## The `read`/`get`/`load`/`fetch` channel

```text
the frames:   {"action":"read","id":"<x>"} / {"action":"get","id":"<x>"} /
              {"action":"load","doc":"<x>"} / {"action":"fetch","item":"<x>"}
the fields:   id / doc / object / item / record / file / path / url
the cells:    the object-IDOR + the LFI (file/path) + the SSRF (url) +
              a `id:"<other>"` cross-principal read
the flag:     another's object OR a file's content
```

## The `history`/`backlog`/`replay` channel

```text
the frames:   {"action":"history","room":"<x>"} / {"action":"backlog"} /
              {"action":"replay","from":0} / {"action":"fetch","since":0}
the fields:   room / channel / conversation / thread / from / to /
              seq / offset / lastEventId / limit
the cells:    a room-IDOR + a seq/offset history-read + a limit-overread
the flag:     another's history/the backlog's flag
```

## The `join`/`subscribe`/`watch`/`listen`/`follow` channel

```text
the frames:   {"action":"join","room":"<x>"} / {"action":"subscribe",
              "channel":"<x>"} / SUBSCRIBE destination:/<x> /
              {"type":"subscribe",<query>}
the fields:   room / channel / topic / destination / namespace / user_id
the cells:    the membership-IDOR + the namespace-membership + the
              subscription-IDOR + the wildcard (#/+)
the flag:     another's feed/the internal channel's pushed flag
```

## The `send`/`dm`/`message`/`chat` channel

```text
the frames:   {"action":"send","to":"<x>","text":"y"} / {"action":"dm",
              "to":"<x>"} / {"action":"message","room":"<x>","text":"y"}
the fields:   to / recipient / target / from / sender / text / msg /
              room / conversation
the cells:    a `to:`/`from:` spoof + a write-side send + a text/msg
              injection (XSS/SSTI via the rendered message) + a
              room-membership gap
the flag:     a write into another's channel / the rendered inject
```

## The `admin`/`debug`/`internal`/`system`/`control` channel

```text
the frames:   {"action":"admin"} / {"action":"debug"} / {"action":
              "internal"} / {"action":"system"} / {"action":"control","cmd":"x"}
the fields:   action / cmd / command / key / value / config / flag
the cells:    the dispatch gap + the config-read/write + a `cmd`/eval/exec
the flag:     the admin/config/flag reply
```

## The `transfer`/`set`/`update`/`grant`/`reset`/`delete` channel

```text
the frames:   {"action":"transfer","to":"me","amount":N} / {"action":
              "set","key":"x","value":"y"} / {"action":"update","id":"<other>"} /
              {"action":"grant","perm":"admin"} / {"action":"reset",
              "user":"admin"} / {"action":"delete","id":"<other>"}
the fields:   to / from / amount / key / value / id / field / perm /
              role / user / account
the cells:    a write-side gap + a transfer-theft + a config-overwrite +
              a grant/reset privilege-escalation + a delete-IDOR
the flag:     a state-change the write caused -> a second read
```

## The `search`/`filter`/`query`/`find`/`sort` channel

```text
the frames:   {"action":"search","q":"<x>"} / {"action":"filter",
              "where":"<x>"} / {"action":"query","q":"<x>"} /
              {"action":"find","q":{<obj>}} / {"action":"sort","order":"<x>"}
the fields:   q / search / query / filter / where / order / sort /
              field / column / match / criteria
the cells:    the injection — sqli/nosqli/order-by-inject/the $operator
the flag:     the injected rows -> the flag column
```

## The `auth`/`login`/`init`/`resume` channel

```text
the frames:   {"type":"auth","token":"<x>"} / {"action":"login",
              "user":"<u>","pass":"<p>"} / {"type":"connection_init"} /
              {"action":"resume","session_id":"<x>"} / 40{"token":"<x>"}
the fields:   token / auth / jwt / user / pass / session_id / resume /
              reconnect / seq / lastEventId
the cells:    a token-forge + a null-token + a session-resumption +
              a stale-token replay
the flag:     a forged/resumed privileged context
```

## The `export`/`dump`/`backup`/`metrics` channel

```text
the frames:   {"action":"dump"} / {"action":"export"} / {"action":
              "backup"} / {"action":"metrics"} / {"action":"config"}
the cells:    a dump/export read — the whole data-surface
the flag:     the dump's flag/secret/key field
```

## The per-channel record

`channel: <the channel>: <the frames>: <the fields>: <the cells>: <the
flag-route>` — the channel's shape names the checks.
