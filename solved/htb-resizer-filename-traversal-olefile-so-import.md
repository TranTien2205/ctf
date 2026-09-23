# Resizer — SOLVED (self-solved)

- Platform: HackTheBox (web). Flask + gunicorn image resizer, Pillow 10.2.0, Python 3.12.
- Date: 2026-09-23
- Target: `http://154.57.164.78:30352`
- Flag: redacted; returned by the resize endpoint itself in the same request
- Worked black-box first, then the source was supplied and confirmed the reading.

## The one bug

`app.py` takes the multipart filename unsanitised:

```python
filename = file.filename
filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)   # UPLOAD_FOLDER = 'uploads'
if os.path.exists(filepath):
    return "File already exists. Please rename your file and try again.", 400
file.save(filepath)
```

That is an arbitrary file write — but **create-only**, because of the exists check.
The extension guard is a substring blacklist:

```python
BLACKLISTED_EXTENTIONS = {'.py', '.pyc'}
if ext in filename: ...        # '.py' matches .py, .pyc, .pyo, .pyw
```

## What does NOT work, and why it is worth knowing

- **Overwriting a template.** `templates/index.html` and `landing.html` contain no
  Jinja at all, so writing `{{ ... }}` into one would be SSTI. Ten path variants
  (`//`, `/./`, trailing slash, `/.`, absolute, `..`-round-trips, case) all hit the
  exists check. It cannot be bypassed.
- **Reading the flag through `send_file`.** The response is
  `send_file(filepath.rsplit('.',1)[0] + '_resized.' + filepath.rsplit('.',1)[1])`
  — i.e. the request path with its **last dot replaced by `_resized.`**. Inverting
  that requires the target to contain `_resized.`, and `/app/flag.txt` does not.
  For the last dot to fall in a directory component instead, the final component
  would have to be dot-free, which `flag.txt` is not. Provably unreachable.
- **ImageMagick tricks.** CVE-2022-44268 does nothing: the output PNG carries only
  IHDR/IDAT/IEND and tEXt chunks are dropped — this is Pillow, not ImageMagick.
- **EPS/Ghostscript.** `.eps`, `.ps` and a real PostScript body all fail at open;
  Ghostscript is not installed.
- **`.pth` in site-packages.** `/usr/local/lib/python3.12/site-packages` is not
  writable by the `app` user, and the user-site directory does not exist.

## What works

`.so` is not blacklisted, and gunicorn puts its working directory on `sys.path`:

```python
# gunicorn/app/base.py
os.chdir(self.cfg.chdir)
if self.cfg.chdir not in sys.path:
    sys.path.insert(0, self.cfg.chdir)     # '/app'
```

Pillow ships a plugin that imports a third-party module which is **not** in
`requirements.txt`:

```python
# PIL/FpxImagePlugin.py:19  (also MicImagePlugin.py:20)
import olefile
```

`Image.init()` imports every `*ImagePlugin`, and `Image.open()` calls `init()` the
first time it meets a file it cannot identify. So uploading any non-image makes
the worker run `import olefile`, which resolves to `/app/olefile.so`.

The payload does not need to be a valid extension module. An **ELF constructor
runs at dlopen, before CPython looks for `PyInit_olefile`**, so the code executes
and the resulting `ImportError` is swallowed by Pillow's plugin loop:

```c
#include <stdlib.h>
__attribute__((constructor))
static void go(void) {
    system("cp /app/flag.txt /app/uploads/zq1_resized.txt 2>/dev/null; ...");
}
```

Rehearsed locally first — `import olefile` raised
`ImportError: dynamic module does not define module export function (PyInit_olefile)`
*after* the constructor had already fired.

The whole thing then lands in **one request**: upload a text file named `zq1.txt`,
which is saved, fails to open as an image, triggers `init()`, runs the payload,
and then `send_file("uploads/zq1_resized.txt")` hands back the flag the payload
just copied there.

## Traps that cost real time

- **An existence oracle that writes.** "File already exists" is a perfect
  file-existence oracle for any path — but on a *miss* it creates the file. Probing
  `../olefile.so` to check whether the payload was in place **overwrote the slot
  with a PNG** and silently disabled the exploit. Probe with names you are willing
  to burn, never with the ones the exploit depends on.
- **The 400 path short-circuits the trigger.** `os.path.exists` returns before
  `file.save` and before the resize, so re-uploading an existing name never runs
  `Image.init()`. Retries must use fresh names or they test nothing.
- **`Image.init()` runs once per process.** Workers that had already met a
  non-image before the payload was planted never import `olefile` again. A fresh
  worker is required.
- **The payload's destination is fixed at compile time.** Both early payloads wrote
  to names whose read slot had already been consumed by earlier testing, so the
  flag was copied somewhere unreadable. Give the payload several destinations.
- Six concurrent 169MP decodes (under Pillow's 2×`MAX_IMAGE_PIXELS` ceiling, so no
  `DecompressionBombError`) killed the workers and **restarted the container**,
  wiping `/app` back to the image. That is destructive — but it is also the only
  delete primitive available, and it is what made the final clean run possible.

## Cleanup performed

`/app/olefile.so` is a working RCE backdoor for anyone who can reach the instance,
and the payload had left four copies of the flag under `uploads/`. Both were
removed by forcing one more container restart; afterwards the trigger no longer
fires, `zq2.txt` no longer returns a flag, and `/` answers 200.

## Reusable lessons

- **When `.py` is blacklisted, look for a missing third-party import instead of a
  writable `.pth`.** Any dependency a library imports but the app never installed
  is a free module slot on whatever directory the server puts on `sys.path`.
- **An ELF constructor beats ABI matching.** A payload `.so` never has to be a real
  Python extension; `__attribute__((constructor))` fires at dlopen and the import
  error afterwards is usually caught by whatever was probing for the module.
- **Decide what the write primitive can and cannot reach before spending it.**
  Working out on paper that `send_file`'s `_resized.` insertion made the flag
  unreachable saved chasing a read that does not exist.
