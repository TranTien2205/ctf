# Sink mining — hunting the vuln in recovered source

## The recovered-source read

When `sourcesContent` reconstructs the real source, read it for the
*sink* — the dangerous operation the challenge wants exploited. The
map recovered the spec; the source shows the vuln.

## The sink taxonomy

```bash
# code execution / eval
grep -rniE '\beval\b|new Function|setTimeout\(["'"'"']|setInterval\(["'"'"']' recovered/
# DOM injection (client-side, -> web-xss via the DOM)
grep -rniE 'innerHTML|outerHTML|dangerouslySetInnerHTML|document\.write|insertAdjacentHTML' recovered/
# deserialization
grep -rniE 'deserialize|unserialize|pickle|yaml\.load|marshal|readObject|ObjectInputStream|JSON\.parse\([^)]*__proto__' recovered/
# command/process
grep -rniE 'exec|spawn|child_process|subprocess|os\.system|Runtime\.getRuntime|ProcessBuilder|shell' recovered/
# file read
grep -rniE 'readFile|file_get_contents|fopen|open\(|Files\.read|sendFile|download' recovered/
# template render
grep -rniE 'render_template|render\(|template|ejs|pug|jinja|freemarker|twig' recovered/
# server-side fetch (SSRF surface)
grep -rniE 'fetch\(|axios\.|http\.get|requests\.(get|post)|urlopen|HttpClient' recovered/
# query construction (injection)
grep -rniE 'query\(|execute|SELECT|INSERT|WHERE|filter|\$where|\.find\(' recovered/
# auth/crypto
grep -rniE 'jwt|sign\(|verify\(|secret|bcrypt|hash|md5|sha1|crypto' recovered/
```

## The sink → class route

| Sink found | Route |
|---|---|
| `eval`/`new Function` on input | `web-command-injection`/`web-ssti` |
| `innerHTML`/`dangerouslySetInnerHTML` | `web-xss` (DOM) |
| `deserialize`/`pickle`/`unserialize` | `web-deserialization` |
| `exec`/`spawn`/`child_process` | `web-command-injection` |
| `readFile`/`file_get_contents`/`sendFile` | `file-read-primitives` |
| `render_template`/template engine | `web-ssti` |
| a server-side `fetch`/`requests.get` | `web-ssrf` |
| a string-built query | `web-sqli`/`web-nosqli` |
| `__proto__`/merge/assign on input | `web-prototype-pollution`/`web-mass-assignment` |

## The client-vs-server sink boundary

A recovered source is the *front-end* — its `innerHTML`/`eval` are
*client-side* sinks (a DOM XSS surface, `web-xss`). The server-side
sinks it names (`fetch` to an endpoint, a `render` call) are *the
client's view of the server* — the endpoint it calls is the target,
and the sink is a hint at what the server does with it.

## The sink-context read

Grep the sink's context (`-B5 -A5`) — what input feeds it, what gate
protects it, what it returns. The sink's surrounding code is the
vuln's contract: the param name, the expected shape, the gate.
