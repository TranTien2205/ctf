# Field inventory — the inputs and outputs, mapped

## The session-create inputs

| Field | Type | Values |
|---|---|---|
| `capabilities.alwaysMatch` | object | the universal capability set |
| `capabilities.firstMatch` | array | alternate capability sets |
| `desiredCapabilities` | object | the legacy form |
| `browserName` | string | `chrome`,`firefox`,`MicrosoftEdge` |
| `browserVersion` | string | a version — Grid selection |
| `platformName` | string | `linux`,`windows`,`mac` |
| `acceptInsecureCerts` | bool | accept self-signed |
| `pageLoadStrategy` | string | `normal`,`eager`,`none` |
| `timeouts` | object | `{script,pageLoad,implicit}` |
| `goog:chromeOptions` | object | Chrome-specific |
| `goog:chromeOptions.args` | array | the Chrome flags |
| `goog:chromeOptions.binary` | string | a binary path |
| `goog:chromeOptions.prefs` | object | profile prefs |
| `goog:chromeOptions.debuggerAddress` | string | attach to a running Chrome |

## The command inputs

| Endpoint | Field | Type |
|---|---|---|
| `POST .../url` | `url` | string — the URL to navigate |
| `POST .../execute/*` | `script` | string — the JS source |
| `POST .../execute/*` | `args` | array — the script's args |
| `POST .../cookies` | `cookie` | object — `{name,value,path,domain,...}` |
| `POST .../element` | `using` | string — `css selector`,`xpath`,... |
| `POST .../element` | `value` | string — the selector |
| `POST .../element/{e}/value` | `text` | string — the text to type |
| `POST .../timeouts` | `script`,`pageLoad`,`implicit` | ints (ms) |
| `POST .../window/rect` | `width`,`height` | ints (px) |

## The outputs

| Endpoint | Output | Shape |
|---|---|---|
| `POST /session` | sessionId + capabilities | `{"value":{"sessionId",...}}` |
| `GET .../url` | current URL | `{"value":"..."}` |
| `GET .../title` | page title | `{"value":"..."}` |
| `GET .../source` | rendered DOM | `{"value":"<html>..."}` |
| `GET .../screenshot` | base64 PNG | `{"value":"<b64>"}` |
| `GET .../cookies` | cookie list | `{"value":[{...}]}` |
| `POST .../execute/*` | the return value | `{"value":...}` |
| `POST .../element` | element handle | `{"value":{"element-6066-...":"id"}}` |
| `GET .../element/{e}/text` | element text | `{"value":"..."}` |
| `GET /status` | driver status | `{"value":{"ready","message",...}}` |

## The flag-carrying fields

| Field | Where | The flag is |
|---|---|---|
| a file's text | `file://` `source` `<pre>` | the file's contents |
| an env var | `file:///proc/self/environ` | `FLAG=...` |
| a cookie | `GET /cookies` or `document.cookie` | the cookie's value |
| a storage value | `localStorage`/`sessionStorage` | the stored string |
| a DOM element | `source`/`execute` `el.textContent` | the element's text |
| a route's body | `localhost/route` `source` | the page's text |
| a rendered image | `screenshot` PNG | the drawn flag |
| an exfil URL/body | your listener's log | the query/body value |
| a same-origin field | the store you read back | the field's value |

## The reproduction fields

| Field | From the bot | Reproduce via |
|---|---|---|
| URL | `goto(url)` arg | `goto(same)` |
| cookie | `setCookie({...})` | `add_cookie({...})` |
| wait | `setTimeout`/`wait_for` | `wait_for_timeout`/condition |
| flags | `args[]` | driver `args` |
| version | `package.json`/Docker | matching browser |
| viewport | `setViewport` | `window/rect` |
