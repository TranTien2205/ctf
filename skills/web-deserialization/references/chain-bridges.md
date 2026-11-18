# Chain Bridges — deser → other bug classes

## The point — deser hands you a primitive, the flag lives elsewhere

A deserialization gadget's *sink* is often the START of a different bug —
the chain crosses classes. This module maps which deser output routes to
which downstream skill.

## The bridge table — deser sink → the next class

| Deser output | The next class | The skill |
|---|---|---|
| URL fetch the server makes | SSRF | `web-ssrf` |
| `file`/`phar` path the server opens | file-read / LFI | `file-read-primitives` |
| a prop that reaches an SQL query | SQLi | `web-sqli` |
| a prop that reaches an `eval`/`render` | code eval / SSTI | `web-ssti` / the eval path |
| a `role`/`is_admin` prop | auth-bypass / IDOR | `web-auth-session` / `web-idor` |
| a written file | file-upload primitive | `web-file-upload` |
| a command-string prop | command injection | `web-command-injection` |
| a URL prop the app redirects to | open-redirect | `web-open-redirect` |
| a class-loader path | phar:// the same class | `phar-deser.md` here |
| a JNDI lookup | JNDI injection | `jndi-injection.md` here |

## deser → SSRF — the URL-fetch gadget

The gadget's sink is a fetch the server makes — `SoapClient.__call` WSDL
fetch, `Guzzle/SSRF1`, a JNDI `lookup`, a `URL.hashCode` — the server just
dialed YOUR URL. That IS an SSRF primitive — and from there the SSRF skill
takes over:

- the URL is yours → `file://`, `gopher://`, `dict://`, cloud metadata,
  internal pivot, redirect
- the fetch is server-side → loopback/internal reachable
- `web-ssrf`'s whole corpus applies to the fetch the gadget makes

## deser → file-read — the getter-reflect chain

A gadget whose sink reads a file and reflects it — `Monolog/FR1`,
`ZendFramework/FR1`, a custom `__toString` that `file_get_contents`s — is
a file-read primitive. From there `file-read-primitives` walks the flag
paths: `/flag`, `flag.txt`, env vars, config files, the app source, the DB
cred — the file the gadget reads is the flag path.

## deser → SQLi — the prop reaching a query

A gadget class whose method builds a query from a prop:

```php
class Report {
    public $table; public $id;
    function run() { $this->db->query("SELECT * FROM {$this->table} WHERE id={$this->id}"); }
}
```

The chain delivers `table`/`id` props — the query is SQLi-shaped → `web-sqli`
payloads apply to the prop's content.

## deser → SSTI / eval — the prop reaching a render

```php
class Page {
    public $template;
    function render() { eval($this->template); }   // or twig_render/sprintf
}
```

The prop is the template/code — the gadget delivers it, the SSTI/eval skill
writes the payload inside it.

## deser → auth-bypass — the prop-only injection

```php
O:8:"User":{role:"admin",id:1}
```

No code — a session/user object whose `role`/`is_admin`/`id` prop you set.
The deserializer instantiates a privileged object the app then trusts →
`web-auth-session`/`web-idor` for what the role unlocks.

## deser → file-upload — the write primitive

A `Guzzle/FW`/`SwiftMailer`/`AspectJWeaver`/`FileUpload1` gadget writes a
file — the file-write IS a file-upload primitive. `web-file-upload`'s
webshell/polyglot/parser tricks apply to where the file lands.

## deser → command-injection — the callable prop

A gadget whose sink is `system($this->cmd)`/`exec($this->arg)` — the prop
IS a command string → `web-command-injection`'s payload-shaping (quoting,
escaping, bypasses) applies to what goes in the prop.

## deser → logic — the role/amount/balance prop

A gadget that sets `balance:999999`/`role:admin`/`verified:true` — a
business-logic prop → `web-logic-flaw`/`web-idor` for what the prop unlocks.

## The reverse bridge — other classes reaching deser

- file-upload → uploads a `.ser` the app unmarshals → deser
- SQLi → a stored object the app reads → second-order deser
- SSRF → reaches a deser endpoint → deser
- session-write → a `$_SESSION` value the app unserializes → deser

## The "the deser WAS the whole bug" check

Not every deser bridges — when the gadget's output IS the flag (a
`cat /flag` RCE, a file-read that reflects `/flag`), the chain ends inside
this class. The bridge modules exist for when the gadget's output is a
*primitive*, not a flag.

## Output to record

- Which deser output was the bridge (file/URL/prop/query)
- Which downstream skill handled the flag-side
- The verbatim evidence for BOTH ends
