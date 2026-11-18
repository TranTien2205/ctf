# Python-Specific Upload Sinks — the interpreter's load surface

## The exec-by-load files — what python picks up automatically

| File | When it runs |
|---|---|
| `sitecustomize.py`/`usercustomize.py` | at interpreter startup (site import) |
| a `.pth` file in site-packages | every startup — lines starting `import ` EXECUTE |
| a `.py` shadowing a stdlib/pkg module | at its import |
| `__init__.py` in a package dir | on package import |
| `conftest.py` | pytest collection — a test run executes it |
| `setup.py`/`pyproject.toml` hooks | `pip install` |
| a pickle file a consumer loads | `web-deserialization` |
| `wsgi.py`/`asgi.py`/app entry | process restart |

## The `.pth` exec — the site-packages line

A `.pth` file's lines starting with `import` run at every interpreter
start:

```python
import os; os.system('id > /tmp/p')
```

Landing `x.pth` into `site-packages/` (traversal or plugin dir) = exec on
the NEXT python process — the app restart, a worker spawn, a cron python.

## `sitecustomize.py` — the always-imported module

Python imports `sitecustomize` after `site` — a writable
`sitecustomize.py` in site-packages or the app's dir = startup exec.

## Module shadowing — `__main__` path injection

```
sys.path = [script_dir, ...stdlib, site-packages]
```

A file named `json.py`, `os.py`, `flask.py` written into a dir earlier in
`sys.path` than the real one shadows it on the next import — the app
crashes or imports your code. Traversal into the app's cwd is the
primitive.

## `conftest.py` — pytest's auto-import

Any dir with `conftest.py` gets it imported when pytest collects — a CI
"run tests" feature + a traversal into the test dir = exec at test time.

## The `pickle`/`dill` file sink — upload feeds a loader

An "import model"/"restore state" endpoint that `pickle.load`s the file —
`skills/web-deserialization/references/python-pickle-deep.md` — `pickle_gen` builds the
artifact:

```bash
python3 tools/pickle_gen.py --cmd 'id > /tmp/x' > x.pkl
```

## The `.py` served vs imported distinction

Same as node: a `.py` in a static dir is text; a `.py` in `sys.path` or
the app's module tree is code. The upload landing spot decides.

## `wsgi.py`/`asgi.py` overwrite — the restart-triggered RCE

Traversal into the app root replacing `wsgi.py`/`app.py`/`main.py` — exec
at next process spawn. `file-overwrite.md` for the write mechanics.

## Falsifiers

- no python-path reach AND no pickle/deser consumer AND no config-file
  sink

## Output to record

- the python-shaped sink reached + its trigger (startup/import/test/build)
