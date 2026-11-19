# Scenarios — the challenge shapes and the pass for each

## Scenario: the live-chat app

```text
the handout: a chat app with wss://x/chat, Socket.IO, a 'history'/
             'dm'/'room' vocabulary
the pass:    1. the handshake origin/binding/samesite cells
             2. 42["history",{"room":"<other>"}] -> a room-IDOR
             3. 42["dm",{"to":"admin","from":"x"}] -> a spoof
             4. 42["broadcast",{...}] -> a cross-client write
the flag:    in another's history/dm OR the broadcast
```

## Scenario: the collaborative doc

```text
the handout: a doc-share with wss://x/doc, 'open'/'op'/'sync'/'version'
the pass:    1. the handshake cells
             2. {"action":"open","doc":"<other>"} -> a doc-IDOR
             3. {"action":"op","doc":"<other>","op":{...}} -> an op-
                injection / a write to another's doc
the flag:    in another's doc
```

## Scenario: the dashboard/metrics

```text
the handout: a live dashboard with wss://x/metrics, 'stats'/'config'/
             'control'/'admin'
the pass:    1. the handshake cells
             2. {"action":"admin"} / {"action":"config","key":"x"} ->
                the privileged dispatch
             3. {"action":"control","cmd":"x"} -> a command gap
the flag:    the admin/config reply
```

## Scenario: the trading/orders

```text
the handout: a trading app with wss://x/trade, 'order'/'balance'/
             'transfer'/'account'
the pass:    1. the handshake cells
             2. {"action":"balance","account":"<other>"} -> an IDOR
             3. {"action":"transfer","from":"<other>","to":"me"} -> a
                write-side theft
the flag:    a balance/transfer read
```

## Scenario: the notifications feed

```text
the handout: a notif service with wss://x/notify, 'subscribe'/'topic'/
             'channel'/'user_id'
the pass:    1. the handshake cells
             2. {"action":"subscribe","user_id":"<other>"} -> another's
                feed
             3. {"action":"subscribe","topic":"internal"} -> an internal
                feed
the flag:    a pushed notification
```

## Scenario: the graphql-over-WS

```text
the handout: a 'subscriptions' endpoint, graphql-transport-ws
the pass:    1. connection_init + authToken
             2. {"type":"subscribe","payload":{"query":"subscription{
                ...}"}} -> a subscription-IDOR/field-leak
             3. a query/mutation inside the frame -> web-graphql
the flag:    a subscription's pushed data
```

## Scenario: the binary/IoT feed

```text
the handout: a binary ws feed / MQTT-over-WS / a protobuf socket
the pass:    1. proto_decode.py the frames -> the field-stream
             2. SUBSCRIBE {#,+} / a device-topic IDOR
             3. a binary command frame -> a control gap
the flag:    a protobuf field / a topic's data
```

## The scenario-record

`scenario: <the shape>: <the pass>: <the flag-route>` — the challenge's
shape names the channel/field set; the pass is the per-shape order.
