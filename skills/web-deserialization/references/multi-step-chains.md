# Multi-Step Chains — when deser is one hop in a longer chain

## The shape — deserialization is rarely the whole exploit

The flag usually sits behind a deser that reaches a SECOND primitive — the
deserializer is the entrance, not the sink. Recognizing the chain's next
step is what turns "RCE" into "the flag".

## The common chain shapes

### deser → file write → include → RCE

```
PHP:  POP writes a .php into webroot  →  GET /shell.php?c=id
Java: AspectJWeaver/FileUpload1 writes a .jsp → GET /shell.jsp?c=
phar: phar:// writes a file → include it via LFI
```

The file-write gadget is the hop — the include/GET is the RCE.

### deser → JNDI → remote classload → RCE

```
JdbcRowSetImpl/C3P0 → lookup → marshalsec serves Exploit.class → RCE
```

The deser only gets to `lookup` — the JNDI server serves the real payload.

### deser → file read → the flag directly

```
Monolog/FR1 / a getter-reflect chain → /flag contents in the response
open('/flag').read() as the pickled value → the value IS the flag
```

### deser → auth bypass → the flag via a protected route

```
O:"User":{role:"admin"}  → the session is now admin
   → GET /admin/flag → the flag behind the auth gate
```

### deser → stored poison → admin-bot fires it

```
write a stored-object the admin's view unserializes
   → admin session/cookie/data leaks via OOB
   → use the admin session to reach the flag
```

### deser → leak the key → forge the real payload

```
a file-read gadget → /app/config → the signing key
   → sign a real gadget → the RCE path
```

## The "reach the flag" decision tree

```
deserializer confirmed
 ├─ can it reach RCE directly?         → os.system/eval/Process.Start
 ├─ can it reach a file write?          → write a webshell → GET it
 ├─ can it reach a file read?           → read /flag directly — cheapest
 ├─ can it reach OOB?                   → fetch/exfil → flag in your log
 ├─ can it reach auth-bypass?           → admin session → the route
 ├─ can it reach a key leak?            → the key → forge a real payload
 └─ none of the above                   → check second-order/JNDI/proxy
```

## The chain-into-itself — a deser inside a deser

A gadget that deserializes ANOTHER serialized value — a nested `unserialize`
inside the chain — the outer gadget's prop is a serialized string the inner
unserializes. Rare but real in CTF handouts built to be multi-hop.

## The "the flag is behind the OTHER class" insight

Sometimes the deserialization only proves a *different* bug — a
`role=admin` prop-injection unlocks an endpoint whose real vulnerability is
SQLi/file-read. The deser class is the delivery, the other class is the
sink — the chain card records both.

## The deser → SSRF bridge — a fetch the chain makes

```
SoapClient.__call → remote WSDL fetch        → SSRF-shaped
Guzzle/SSRF1      → URL fetch                 → SSRF
JdbcRowSetImpl    → JNDI lookup               → JNDI/SSRF
url fetch gadget  → a fetch the server makes  → reaches internal
```

A deserialization gadget whose sink is a URL fetch IS an SSRF primitive —
`web-ssrf` takes over from there (cloud metadata, internal pivot, gopher).

## The deser → template/code-eval bridge

```
a gadget whose sink calls eval/render/compile on a prop → code eval
Monolog/FW → a file-write → include → exec
TemplatesImpl → defineClass → static block → exec
```

The "deserialization" ends at a template/eval/engine call — the SSTI/eval
skill's payload becomes the prop.

## The "two teams" chain — the attack-defense shape

On attack-defense (sibling mode — `tools/ad/`), a planted deserialization
backdoor is a *defense* problem — find the `unserialize`/`readObject` in
the service code the organiser shipped. The offensive chain is the same —
the goal is different (patch + don't lose the SLA).

## The kill-chain map — the order the record takes

```
entry:    the endpoint/param/cookie carrying the blob
format:   the magic bytes identified
reach:    corrupt-diff → parser confirmed
probe:    marker/URLDNS/OOB → deserializer confirmed
version:  classpath measured → chain picked
gadget:   the chain fired
sink:     RCE / file-write / file-read / OOB / auth-bypass
flag:     the verbatim flag-bearing response/OOB line
```

## Output to record

- The full chain: entry → format → gadget → sink → flag
- Which hop the deser provided vs which was a different primitive
- The verbatim flag-bearing response/OOB excerpt
