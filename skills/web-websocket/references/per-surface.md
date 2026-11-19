# Per surface — each surface, its channels, its checks

## The chat/DM surface

- channels: `history`/`dm`/`room`/`conversation`/`thread`
- fields: `room`/`id`/`to`/`from`/`msg`/`text`
- the gaps: a DM/room IDOR, a broadcast, an `history` over-read, a
  `to:`/`from:` spoof
- probes: `{"action":"history","room":"<other>"}`, `{"action":"dm",
  "to":"admin"}`, `{"from":"victim","msg":"x"}`

## The notification/presence surface

- channels: `notify`/`presence`/`online`/`status`/`events`
- fields: `user_id`/`channel`/`subscribe`/`topic`
- the gaps: a cross-user notification read, a presence-IDOR, a
  subscription to another's feed
- probes: `{"action":"subscribe","user_id":"<other>"}`,
  `{"action":"notify","user_id":"<other>"}`

## The collaborative-edit surface

- channels: `doc`/`edit`/`sync`/`op`/`cursor`/`selection`
- fields: `doc`/`op`/`user_id`/`version`/`content`
- the gaps: a doc-IDOR, an `op`-injection, a `user_id`-spoof on an op
- probes: `{"action":"open","doc":"<other>"}`, `{"action":"op","doc":"
  <other>","content":"x"}`

## The game/lobby surface

- channels: `lobby`/`game`/`move`/`state`/`spectate`
- fields: `game_id`/`room`/`player`/`move`/`action`
- the gaps: a game-state read, a move-spoof, a lobby-membership IDOR
- probes: `{"action":"join","room":"<other>"}`, `{"action":"move",
  "game_id":"<other>"}`

## The dashboard/admin surface

- channels: `metrics`/`admin`/`stats`/`config`/`control`
- fields: `action`/`cmd`/`config`/`key`/`value`
- the gaps: an admin-action dispatch, a config-read/write
- probes: `{"action":"admin"}`, `{"action":"config","key":"x"}`

## The trading/finance surface

- channels: `order`/`trade`/`balance`/`position`/`market`
- fields: `account`/`order`/`amount`/`to`/`from`
- the gaps: a balance-IDOR, a transfer, an order-spoof
- probes: `{"action":"balance","account":"<other>"}`,
  `{"action":"transfer","to":"me","amount":N}`

## The IoT/telemetry surface

- channels: `sensor`/`telemetry`/`device`/`control`/`topic`
- fields: `device`/`topic`/`cmd`/`payload`
- the gaps: a device-topic IDOR, a control-command, a `SUBSCRIBE #`
- probes: `{"action":"subscribe","topic":"#"}`, `{"action":"cmd",
  "device":"<other>"}`

## The per-surface record

`surface: <name>: <the channel>: <the fields>: <the oracle cells>` —
the surface names the channel/fields to probe; the coverage matrix is
per-surface.
