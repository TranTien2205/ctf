# DLLAMA — SOLVED

- HackTheBox challenge 783, web. Description: a hidden LaTeX application.
- Flag read from a live response: `HTB{REDACTED}` (extracted from the text layer of the generated PDF).
- Assistance: writeup-assisted. The pickle cookie, the authentication bypass and the LaTeX blacklist were found independently; the `^^xx` encoding bypass and the `\verbatiminput` read were taken from public writeups after the naive payload was blocked.

## Stack

- Flask / Werkzeug / Python 3.11.
- A passwordless login form (username only) sets a `user` cookie that is a base64 Python pickle of `__main__.User(username=..., authenticated=False)`.
- The home page, once authenticated, renders a LaTeX-to-PDF form that posts `latex_code` to `/`.
- The generated PDF is served at `/static/input.pdf`.
- A blacklist rejects `\`, `{`, `}`, `%`, `$`, `#`, `|`, `"`, `&` and the LaTeX commands.

## Chain

1. Log in with any username. The response sets `user=<base64 pickle of __main__.User>`.
2. `pickletools.dis` shows a `__main__.User` object with `username` and `authenticated` attributes.
3. Forge the pickle with `authenticated=True` and send it back. `/` now returns the authenticated LaTeX-to-PDF form instead of the login redirect.
4. The blacklist blocks every LaTeX special character, so a plain injection is rejected. LaTeX expands `^^xx` hexadecimal escapes during tokenisation, and `^` is not blacklisted.
5. Encode the whole document character by character as `^^xx` and submit it. The blacklist sees only `^` and hex digits.
6. The document uses `\usepackage{verbatim}` and `\verbatiminput{flag.txt}` to inline the flag file into the PDF.
7. Fetch `/static/input.pdf` and extract the text layer to read the flag.

## Reusable

- A cookie that is a base64 pickle is an unsafe-deserialization trust boundary; forging the object's attributes is enough to cross it when only an auth flag is checked.
- A LaTeX blacklist that only filters literal characters is bypassed by `^^xx` hex escapes, which the TeX input processor expands after the filter runs.
- `\verbatiminput{file}` inlines a file into the PDF without any `\input` or shell escape.

## Traps

- The pickle RCE via `__reduce__` did not run here; the object is type-checked after load, so attribute forgery was the working route.
- The naive `\input{|"id"}` payload is blocked by the blacklist; the `^^xx` form is required.
- The generated PDF is written to a predictable path (`static/input.pdf`) and stays there; overwrite it with a benign document afterwards so the flag is not left on the shared instance.
- The flag file is `flag.txt` relative to the application directory.
