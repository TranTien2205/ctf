# Error Analysis — read the parser's complaint

## The rule — an error message is a fingerprint, not a failure

Every deserializer errors differently. The string in the 500 body tells you
WHICH parser ran, WHAT it expected, and WHICH class/version it wanted. A
deserialization "failure" is usually a version mismatch that *names* the
right version.

## PHP

```
unserialize(): Error at offset 4 of 23 bytes
  → PHP grammar broke at byte 4 — your length count is off
__PHP_Incomplete_Class_Name in /app/x.php
  → allowed_classes stripped it, or the class isn't autoloaded
Object of class X could not be converted to string
  → a __toString was expected — your object lacks it
unserialize(): ExpectedClass but got OtherClass
  → class-name mismatch
Allowed memory size / Maximum execution
  → chain fired but hung — a gadget loop
```

## Java — the serialVersionUID oracle

```
java.io.InvalidClassException: com.app.Foo;
  local class incompatible: stream classdesc serialVersionUID = -5195,
  local class serialVersionUID = 7637
  → the CLASS EXISTS at a DIFFERENT version — the exception tells you the
    expected UID; regenerate the chain against that jar version
java.lang.ClassNotFoundException: org.apache.commons.collections.functors.ChainedTransformer
  → that LIBRARY is NOT on the classpath — pick a different chain
java.io.StreamCorruptedException: invalid stream header: 3C3F786D
  → not a real OIS blob — that's `<?xm` ASCII (you sent XML, not binary)
java.io.InvalidObjectException / filter: REJECTED
  → JEP-290 ObjectInputFilter / a resolveClass whitelist is live
```

## Python pickle

```
_pickle.UnpicklingError: pickle data was truncated
  → your stream is cut short — check the wrapper/length
_pickle.UnpicklingError: invalid load key, 'x'
  → byte isn't an opcode — wrong format or corrupted
AttributeError: Can't get attribute 'PWNED_X1' on <module '__main__'>
  → loads() ran, your class name reached find_class — CONFIRMED
_pickle.UnpicklingError: GLOBAL 'os.system' is forbidden
  → find_class whitelist is live — use builtins paths
TypeError: __reduce__() must return a string or tuple
  → your __reduce__ shape is malformed
EOFError / ValueError: insecure pickle
  → the app runs a checker before loads — the checker's own signature
```

## Ruby Marshal / Psych

```
ArgumentError: dump format error (0x4f)
  → byte 0x4f isn't a valid type tag — Marshal reached your bytes
TypeError: incompatible marshal file format
  → version byte wrong — Marshal.load confirmed
Psych::DisallowedClass: Tried to load unspecified class: Gem::Requirement
  → safe_load rejected the tag — but it REACHED the loader → confirm format,
    find a permitted_class that reaches a gadget
```

## .NET

```
System.Runtime.Serialization.SerializationException:
  End of Stream encountered before parsing was completed
  → BinaryFormatter reached your bytes — CONFIRMED
System.Web.UI.ViewStateException: Invalid viewstate
  → LosFormatter/MAC — the ViewState is intact but MAC failed
Newtonsoft.Json.JsonException: Error resolving type specified in JSON 'X'
  → Json.NET TypeNameHandling is ON — the $type was parsed
Newtonsoft.Json.JsonSerializationException
  → type resolved but couldn't construct — wrong ctor shape
```

## YAML loaders

```
yaml.constructor.ConstructorError: could not determine a constructor
  for the tag 'tag:yaml.org,2002:python/object:os.system'
  → PyYAML unsafe path reached your tag — CONFIRMED
yaml.YAMLError + "found character '%'"   → syntax break, not deser
Global constructor is not allowed        → Snakeyaml SafeConstructor
Psych::DisallowedClass                   → Psych safe_load
org.yaml.snakeyaml.error.YAMLException   → Snakeyaml reached
```

## Node

```
SyntaxError: Unexpected token      → JSON.parse broke, not deser
TypeError: x is not a function     → revived but not invoked — add ()
Error: Cannot find module 'x'      → revived require ran — confirm format
```

## The reading order

```
1. is the error a PARSER signature or a generic 500?
2. does it name a class/version/offset — that's free fingerprinting
3. does it say "rejected"/"forbidden"/"not allowed"? → a filter is live
4. does it say "incompatible"/"ClassNotFound"/"not found"? → version/path
   mismatch — the class state is leaked, fix the chain
```

## The useful-error trick

Send a blob naming a class the app can't have — `com.attacker.Probe`,
`Attacker\Probe`, `__main__.Probe` — the error names YOUR class back =
the parser built it / tried to resolve it = deserializer confirmed. This is
the single cheapest confirmation that works on every format.
