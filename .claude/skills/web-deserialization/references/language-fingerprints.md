# Language Fingerprints — the micro-tells in the blob itself

## The point — two blobs can both look "serialized" but mean different things

`O:8:"User":...` is PHP. `O:8` is ALSO a possible pickle-fragment or an
XML attribute. The fingerprint is the *grammar* not the prefix — this is the
fine-grained discriminator.

## PHP — the grammar signatures

```
O:<len>:"<name>":<count>:{<props>}   — the object shape
a:<n>:{...}                           — array — always balanced braces
s:<len>:"<bytes>";                    — string — the ; terminates
S:<len>:"<bytes>";                    — escaped string
i:<int>;   b:<0|1>;   N;              — scalars
d:<float>;                            — float
R:<n>;  r:<n>;                        — references
C:<len>:"<cls>":<len>:{<opaque>}      — Serializable-class blob
```

The *terminating semicolon* and the balanced `{}` are the grammar — a
truncated `O:4:"User"` without `{` is a partial, not a valid PHP stream.

## Java — the TC_* grammar

```
AC ED 00 05                           — header + version (always 5)
74 = TC_OBJECT   72 = TC_CLASSDESC   71 = TC_REFERENCE
70 = TC_NULL     76 = TC_STRING      75 = TC_ARRAY
73 = TC_CLASS    78 = TC_BLOCKDATA   79 = TC_ENDBLOCKDATA
7A = TC_RESET    7E = TC_ENUM        7B = TC_EXCEPTION
```

The classdesc carries `classDescFlags` + field count + field table +
classAnnotation (until ENDBLOCKDATA) + superClassDesc — `java-deep.md` has
the full grammar. A `aced` that isn't followed by a TC_* byte isn't a stream.

## Python pickle — the opcode grammar

```
\x80\x03 / \x80\x04 / \x80\x05         — protocol marker (p3/p4/p5)
c<mod>\n<attr>\n                       — GLOBAL
S'x'\n / V / \x8c / X                  — string opcodes
)  EMPTY_TUPLE    t  TUPLE    .  STOP  — structure
R  REDUCE         b  BUILD    \x81 NEWOBJ
q/h/j/r                              — memo ops
```

A pickle is a PROGRAM — the opcodes are the tell. `pickle_dis.py` walks them.
An `80 03` with no valid opcode after is not a pickle.

## Ruby Marshal — the typed tags

```
\x04\x08          — the 4.8 version marker
o:  object        O:  object-with-ivars     u:/U:  usermarshal
I  ivars          :  symbol         ;  symbol-link
"  string         i  integer        [  array   {  hash
S:  struct        c  class          m  module  e  extended
f  float          /  regex          l  bignum  T/F/nil
```

`BAh` in base64 = `\x04\x08`. A `\x04\x08` followed by a non-tag byte is
not a Marshal stream.

## .NET — the formatter markers

```
00 01 00 00 00 FF FF FF FF        — BinaryFormatter root record
01 = serialization header record type
AAEAAAD/////                       — the b64 shape of the above
/wEP                               — ViewState (LosFormatter)
<SOAP-ENV:Envelope                 — SoapFormatter
{"$type": / {"__type":             — Json.NET/JavaScriptSerializer
<root z:Type=...                   — NetDataContractSerializer
```

## YAML — the tag grammar

```
!!python/object:app.Cls            — PyYAML unsafe
!!python/object/apply:os.system    — PyYAML apply
!!python/name:module.attr          — PyYAML name
!!javax.script.ScriptEngineManager — Snakeyaml
!!com.sun.rowset.JdbcRowSetImpl    — Snakeyaml JNDI
!ruby/object:ERB                   — Psych
!ruby/struct:Cls                   — Psych struct
!!js/function 'code'               — js-yaml ≤3
!<tag:yaml.org,2002:...>           — the explicit-tag form
```

## Node — the revive markers

```
_$$ND_FUNC$$_function(){...}()     — node-serialize
$$__FUNCTION__$$                   — funcster
!!js/function 'code'               — js-yaml ≤3
{"py/object":"mod.Cls"}            — jsonpickle
{"meta":{"...":"..."}}             — superjson
{"$type":"..."}                    — Json.NET-style
```

## The "it's not that format" disambiguation

| Looks like | Actually is |
|---|---|
| `O:8:"User"` | PHP — the `":`+count+`{` grammar |
| `{"a":1,"O":"x"}` | JSON — the `O` is a key, not a type tag |
| `aced` in a hex dump | could be Java OR coincidental hex — check for TC_* |
| `gAN` in base64 | pickle p3 — but a coincidental b64 prefix happens — check opcodes |
| `BAh` in base64 | Marshal — check `\x04\x08` after decode |
| `<object class=` | XMLDecoder/XStream |
| `<SOAP-ENV` | SoapFormatter or plain SOAP |
| `rO0AB` | Java b64 — `rO0AB`+5th-char varies |

The grammar bytes AFTER the prefix decide — a `Tzo` b64 prefix that decodes
to `O:` grammar is PHP; a `Tzo` that decodes to garbage is a coincidence.

## The multi-layer fingerprint — wrapped formats

```
b64(urlencode(O:...))          → unwrap: unurl → deb64 → PHP grammar
b64(gzip(aced...))             → deb64 → gunzip → Java stream
{"d":"<b64 O:>"}               → json → deb64 → PHP grammar
__VIEWSTATE=<b64(losformatter+mac)>  → LosFormatter + MAC
```

Fingerprint the INNER layer after peeling — `encoding-channels.md` is the
wrapper module.

## Output to record

- The magic bytes found + the format they imply
- Which grammar element confirmed it (the `{`, the TC_*, the opcode, the tag)
- The module the fingerprint routes to
