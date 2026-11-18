# Misc Formats — RSS / XMPP / plist / config / other XML-in-disguise

## RSS / Atom import — feed parsers

```xml
<?xml version="1.0"?>
<!DOCTYPE rss [<!ENTITY x SYSTEM "file:///flag">]>
<rss version="2.0">
  <channel><title>&x;</title><link>x</link><description>&x;</description>
  <item><title>&x;</title></item></channel>
</rss>
```

- `<title>`/`<description>`/`<link>`/`<guid>` — echoed in feed previews
- Atom: `<feed xmlns="http://www.w3.org/2005/Atom">` — same shape
- OPML (feed-reader import): `<opml><body><outline text="&x;"/>`

## XMPP / Jabber — stanzas ARE XML

```
<message to='x'><body>&x;</body></message>
<iq type='get'><query xmlns='jabber:iq:roster'/></iq>
```

XMPP servers/clients parse XML stanzas — a CTF XMPP service accepts
crafted stanzas → entity expansion inside `<body>`/`subject` etc.
Stream-level XXE (the `<stream:stream>` wrapper) — niche.

## `.plist` — Apple property lists are XML

```xml
<?xml version="1.0"?>
<!DOCTYPE plist [<!ENTITY x SYSTEM "file:///flag">]>
<plist version="1.0"><dict><key>k</key><string>&x;</string></dict></plist>
```

Any macOS/iOS-adjacent app accepting `.plist` — or web "import
settings" for plist.

## `.xml` config upload — `.config`/`web.config`/`pom.xml`/`build.xml`/`.csproj`/`packages.config`/`web.xml`/`struts.xml`/`.resx`/`.manifest`

- `web.config`/`app.config` — .NET app config — parsed with
  `XmlDocument`/`XmlReader` — XXE in `<appSettings>` values
- `pom.xml`/`build.xml`/`ivy.xml`/`settings.xml` — Java build files —
  Ant/Maven/Ivy parse them
- `.csproj`/`.vbproj`/`.fsproj` — MSBuild XML — MSBuild resolves
  entities on import
- `web.xml`/`struts.xml`/`context.xml`/`server.xml` — Java EE configs
- `.resx`/`.manifest`/`.xaml`/`App.config`/`packages.config` — .NET
- `docbook`/`dita` — doc pipelines

Any "import config"/"deploy descriptor" upload surface.

## `.docx`-adjacent niche formats — `.xodt`/`.xps`/`.epub`/`.odp`/`.odp`/`.docm`/`.xlam`/`.ppam`/`.cbz`/`cb7`/`.docbook`

- `.epub` — ZIP of XHTML — `OEBPS/content.opf` + `*.xhtml` — XXE in
  `<package>`/`manifest`/`spine`/`ncx`
- `.xps`/`OpenXPS` — XML pages
- `.cbz`/`.cb7` — comic archives (may contain .xml metadata)
- `.musicxml` — music notation XML
- `.gpx`/`.kml` — GPS XML — mapping apps
- `.xspf` — playlist XML
- `.maven`/`ivy.xml`/`pom.xml` — build dep files
- `.xib`/`.storyboard`/`.nib` — Xcode UI XML
- `.drawio`/`.dio` — drawio XML
- `.gliffy` — diagram XML
- `.xmind` — mindmap ZIP+XML
- `.mm` — FreeMind XML
- `.wsdd` — axis deployment
- `.pom`/`.ivy`/`.sbt` — build
- `.bpmn` — BPMN XML
- `.xlf`/`.xliff` — localization
- `.ts`/`Qt .ts` — Qt translation XML
- `.nmap`/`.nessus` — scan XML — "import scan results" features

## The "the XML is inside another format" — nested parsing

- PDF → XMP metadata (`xpacket` rdf) → XML parse
- JPEG/PNG metadata → XMP blocks inside → XML parse by tools
- .jar `META-INF/*.xml`/`web.xml` — Java archive XML
- `.eml` with `.xml` attachments
- `.p12`/`.jks` — no. skip.

## The "it's not even a file — it's a field that parses XML" — SOAP-adjacent

- a form field that takes an XML snippet ("enter your config XML")
- a SOAP `Detail`/`Header` sub-element
- an HTML `<xml>` data-island (`<xml id="x">` — legacy IE) — browser-side

## Falsifiers

- the app only accepts binary formats / the XML part gets sanitized —
  class dead on that surface
