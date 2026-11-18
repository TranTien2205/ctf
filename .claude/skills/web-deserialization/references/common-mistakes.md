# Common Mistakes — the ways this class burns budget

## 1. Firing a gadget before confirming the sink

The #1 budget-killer. A `CommonsCollections5` error on an app that never
unserializes proves nothing. Corrupt-and-diff FIRST — a parser signature on
your bytes is the cheapest confirm in the class.

## 2. Hand-counting PHP property lengths

`O:4:"User":2:{s:4:"name";s:5:"admin";}` — count `"admin"` as 4 and the
grammar breaks at offset N. Private props carry `\0CLASS\0` prefixes you
can't see in a terminal. `php_ser_gen.py --spec` counts for you — use it.

## 3. Forgetting the `()` on node-serialize

`_$$ND_FUNC$$_function(){...}` without trailing `()` revives the function
but never calls it — silent. The IIFE is the whole exploit.

## 4. Picking a chain for the wrong library version

CC1 on commons-collections3.2.2, a Laravel/RCE1 on Laravel 8 — the
`InvalidClassException`/`local class incompatible` error NAMES the expected
serialVersionUID → read it, it's telling you the version.

## 5. `pickle.loads`ing a suspect blob to inspect it

That IS the exploit. `tools/pickle_dis.py` walks the opcodes — never loads.

## 6. Trusting a signature-bypass claim that wasn't made

"alg=none might work" is not a measurement. Send it, read the response. The
`alg=none`/confusion/kid tests are each one probe — spend them.

## 7. Aiming at the flag before the class is proven

`os.system('cat /flag')` on an unconfirmed sink wastes a probe AND leaks
your intent. Marker/URLDNS first — prove `readObject`/`unserialize` ran,
THEN spend a gadget.

## 8. Treating `allowed_classes`/`safe_load` as a hard wall

`allowed_classes` still permits the LISTED classes — a whitelisted class
with a magic method is the gadget. `safe_load`+`permitted_classes=[Symbol]`
still revives Symbols. Read what the filter permits, not just that it exists.

## 9. Missing the second-order read

The blob is STORED verbatim on write — the deserializer is on a DIFFERENT
read path (admin view, worker, cache get). A clean write-response is not a
falsifier — find the consumer.

## 10. Base64-decoding only once

`b64(b64(blob))`, `url(b64(blob))`, `hex(gzip(blob))` — unwrap until the
magic bytes show. `rO0AB` inside `eyJ` inside a cookie is three layers.

## 11. Confusing serializer formats

- `itsdangerous` JSON vs `itsdangerous` pickle — check `gAN`/`eyJ` inside
- PHP `serialize` vs `igbinary` vs `session.serialize_handler=php` —
  different containers, same-ish grammar
- `XmlSerializer` vs `BinaryFormatter` — XmlSerializer is setter-only

## 12. Forgetting `S:` for the addslashes/`'` case

`s:` can't carry a literal NUL/quote through a mangle — `S:` hex-escapes
every byte. `php_ser_gen.py --str-type S` emits it.

## 13. Claiming a timeout as a hit

A slow response might be WAF/throttle/crash — never evidence. Only a parser
signature, a callback, or a marker confirms.

## 14. Missing `__wakeup` suppression

A chain whose entry is `__destruct` but a `__wakeup` resets the props —
try the prop-count lie (`O:4:"X":3:{2 props}`) to skip `__wakeup` on
PHP <5.6.25/7.0.10.

## 15. Not checking `phar.readonly` correctly

`phar.readonly=On` (default) blocks CREATING phars server-side — it does
NOT block phar:// READING on an uploaded one. The attack still works.

## 16. Missing the JNDI JDK-version gate

`ldap://` works ≤8u190, dead ≥8u191 — on a modern JDK use `javaSerializedData`,
Tomcat BeanFactory, or `JdbcRowSetImpl`-in-a-chain, not a raw ldap URL.

## 17. Assuming JSON.parse is deserialization

`JSON.parse` builds data, never objects-with-code. `node-serialize`/
`funcster`/a custom reviver is the sink — plain `JSON.parse` is a falsifier.

## 18. Not reading `serialVersionUID` errors as fingerprint

`local class incompatible: stream classdesc UID=-X, local class UID=Y` —
the error tells you the class exists at a different version. A useful error.
