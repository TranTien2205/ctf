# Per-sink — each recovered-source sink and its class

## The code-execution sink

| Sink | Route |
|---|---|
| `eval(`, `new Function(` | `web-command-injection`/`web-ssti` |
| `setTimeout("...")`, `setInterval("...")` | `web-command-injection` |
| `exec(`, `spawn(`, `child_process`, `subprocess`, `os.system`, `Runtime.exec`, `ProcessBuilder` | `web-command-injection` |

## The DOM/render sink

| Sink | Route |
|---|---|
| `innerHTML`, `outerHTML`, `document.write`, `insertAdjacentHTML`, `dangerouslySetInnerHTML` | `web-xss` (DOM) |
| `render_template`, `render(`, `template(`, `ejs`, `pug`, `jinja`, `freemarker`, `twig`, `handlebars` | `web-ssti` |

## The deserialize sink

| Sink | Route |
|---|---|
| `deserialize`, `unserialize`, `pickle.loads`, `yaml.load`, `marshal`, `readObject`, `ObjectInputStream`, `JSON.parse` on `__proto__` | `web-deserialization`/`web-prototype-pollution` |

## The fetch/SSRF sink

| Sink | Route |
|---|---|
| `fetch(`, `axios.get`, `requests.get`, `http.get`, `urlopen`, `HttpClient.get` on a controllable URL | `web-ssrf` |

## The file-read sink

| Sink | Route |
|---|---|
| `readFile`, `file_get_contents`, `fopen`, `open(`, `Files.read`, `sendFile`, `download`, `readFileSync` | `file-read-primitives` |

## The query sink

| Sink | Route |
|---|---|
| `query(`, `execute(`, string-built `SELECT`/`WHERE`, `.find(` on an object, `$where` | `web-sqli`/`web-nosqli` |

## The auth/crypto sink

| Sink | Route |
|---|---|
| `jwt.sign`/`verify` with a weak/`none` alg | `web-auth-session` |
| `md5`/`sha1` on a token | `web-auth-session`/`crypto` |
| a hardcoded `secret`/`key` used in `sign` | `web-auth-session` |

## The merge/assign sink

| Sink | Route |
|---|---|
| `Object.assign`, `merge(`, `extend(`, `_.merge`, `$.extend` on user input | `web-prototype-pollution`/`web-mass-assignment` |

## The redirect sink

| Sink | Route |
|---|---|
| `redirect(`, `window.location = `, `header("Location`, `res.redirect` on a param | `web-open-redirect` |

## The client-vs-server note

A recovered source is the *front-end* — `innerHTML`/`eval` are
*client-side* sinks (a DOM-XSS surface). The server-side sinks it names
(`fetch` to an endpoint, a `render` call) are the *client's view of the
server* — the endpoint it calls is the real target, the sink is the
hint at what the server does with it.
