# Per-surface map — each surface's shape → the cells

## The chat/DM surface

```text
the frames:   history / dm / room / conversation / thread / send /
              message / broadcast / announce
the fields:   room / channel / conversation / to / from / sender /
              msg / text / id
the cells:    a room/conversation IDOR + a history-IDOR + a
              broadcast-blast + a from/to spoof + a text/msg inject +
              a write-side send
the flag:     another's history/dm / a broadcast flag
```

## The doc/collab surface

```text
the frames:   open / op / sync / version / edit / cursor / selection /
              save / load / share
the fields:   doc / document / op / user_id / version / content /
              field / change / patch
the cells:    a doc-IDOR + an op-injection + a user_id spoof on an op +
              a version/history read + a content inject
the flag:     another's doc content
```

## The notification/presence surface

```text
the frames:   subscribe / notify / presence / online / status / events /
              typing / read / seen
the fields:   user_id / channel / subscribe / topic / status / event /
              type
the cells:    a cross-user notification read + a presence-IDOR + a
              subscription to another's feed + a status/write gap
the flag:     a pushed notification's data
```

## The dashboard/metrics/admin surface

```text
the frames:   stats / metrics / admin / config / control / system /
              monitor / health
the fields:   action / cmd / command / config / key / value / metric /
              name
the cells:    the dispatch gap + the config-read/write + a cmd/exec +
              an internal/system action
the flag:     the admin/config/flag reply
```

## The trading/finance surface

```text
the frames:   order / trade / balance / position / market / transfer /
              withdraw / deposit / portfolio
the fields:   account / order / amount / to / from / price / quantity /
              asset / symbol
the cells:    a balance/account IDOR + a transfer-theft + an order-spoof +
              an amount/price field
the flag:     a balance/transfer read / a privileged account
```

## The game/lobby surface

```text
the frames:   lobby / game / move / state / spectate / join / ready /
              score / board
the fields:   game_id / room / player / move / action / score / board /
              turn
the cells:    a game-state read + a move-spoof + a lobby-membership IDOR +
              a score/board write
the flag:     the game-state's flag / a privileged move
```

## The IoT/telemetry surface

```text
the frames:   sensor / telemetry / device / control / topic / cmd /
              payload / status / config
the fields:   device / topic / cmd / payload / sensor / control / value
the cells:    a device-topic IDOR + a control-command gap + a SUBSCRIBE
              #/+ wildcard + a cmd/payload inject
the flag:     a device/topic's data / a control-cmd
```

## The graphql surface

```text
the frames:   connection_init / subscribe / start / next / complete /
              connection_ack
the fields:   type / payload / query / authToken / id / operationName /
              variables
the cells:    a subscription-IDOR + a field-leak + a mutation-in-frame +
              an introspection
the flag:     the subscription's pushed field
```

## The search/filter surface

```text
the frames:   search / filter / query / find / sort / list / paginate
the fields:   q / search / query / filter / where / order / sort /
              field / column / match / criteria / page / limit / offset
the cells:    a sqli/nosqli/order-inject + a pagination overread + a
              field/column selection gap
the flag:     the injected rows / the paginated flag
```

## The per-surface record

`surface: <the name>: <the frames>: <the fields>: <the cells>: <the
flag-route>` — the surface's shape names the cells.
