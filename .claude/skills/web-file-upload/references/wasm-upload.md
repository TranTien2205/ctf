# WASM / Shared-Library Upload — the code-blob primitive

## The shape — a compiled artifact that runs

`.wasm`, `.so`, `.dll`, `.dylib`, `.pyc`, `.class`, `.node` — a compiled
binary that gets loaded by a runtime. The upload is the code blob —
exec requires the loader to run it.

## `.wasm` — browser or server-side

- browser: `WebAssembly.instantiate(fetch('x.wasm'))` — sandboxed,
  limited impact — client-side only
- server: `wasmtime`/`wasmer` run it with host functions — a `wasi` import
  can reach `fd_write`/`proc_exit`/`sock` — the sandbox's WASI config
  decides impact
- a `.wasm` that imports `wasi_snapshot_preview1` syscall-like functions
  — sandboxed syscall surface

## `.so`/`.dll`/`.dylib` — native library load

- python `ctypes.CDLL('x.so')`/`cffi.dlopen` — a "load this extension"
  feature = native RCE
- php `extension=x.so` in `.user.ini`/`php.ini` — loads the lib at startup
- node `require('x.node')` — a native addon — N-API execs on load
- a `.so` dropped where `dlopen`/`LD_LIBRARY_PATH`/`DT_RPATH` picks it —
  `.so` in a lib-dir traversal = exec on next load

The `.so` upload is dangerous anywhere a loader reads it — the
`constructor`/`_init`/`__attribute__((constructor))` sections run at
`dlopen` time, not when functions are called.

```c
__attribute__((constructor)) void init() { system("id > /tmp/x"); }
```

## `.pyc` — compiled python

A `.pyc` upload into `__pycache__/` or where an import hits it — exec on
import. `__pycache__/x.cpython-3X.pyc` name matters (the tag).

## `.class`/`.jar` — the JVM side

`jar-war-deploy.md` — the class execs on load by a servlet/plugin loader.

## `.node` — native addon

`require('x.node')` — N-API module — `NAPI_MODULE_INIT` runs at load —
the import IS the exec.

## The "load this file" endpoints — which features accept binary blobs

- `upload model` — `.pt`/`.pkl`/`.onnx` → `torch.load`/`pickle` — deser
- `upload extension/plugin` — `.so`/`.dll`/`.node` → native load
- `upload wasm` — instantiate
- `upload .pyc`/`upload .class` — bytecode load
- `dlopen`/`require`/`load_extension`/`import_module` on a path param —
  the file path is attacker-controlled AND loaded

## Detection — is there a load step?

- upload goes to `/uploads/` and is served — static, no load → static-side
  only
- upload gets `import`ed/`require`d/`dlopen`ed/`load`ed — binary exec
- check source for `dlopen`/`LoadLibrary`/`CDLL`/`load_module`/
  `importlib.import_module`/`require`/`torch.load`/`pickle.load` on a
  path derived from the upload

## Falsifiers

- the file is only stored/served, never loaded/executed — the load step
  doesn't exist
- the loader is sandboxed with no host-function reach (pure `.wasm` with
  no WASI, no imports)

## Output to record

- which loader consumes the file + what it does with the loaded artifact
