# Node/JS-Specific Upload Sinks — the npm-shaped primitives

## The hooks — files npm/node loads on action

| File | When it executes |
|---|---|
| `package.json` `scripts` | `npm install`/`npm run`/`npm test` — pre/post hooks |
| `.npmrc` `script-shell`/`prepack` | npm config affecting commands |
| `node_modules/<pkg>/` | `require()` resolves it |
| `.nvmrc`/`.node-version` | version manager picks runtime |
| `index.js`/`main` | default module entry |
| `server.js`/`app.js` | process startup |
| `.babelrc`/`.mocharc`/`jest.config` | tool config with code paths |
| `webpack.config.js`/build config | build-time exec |
| `tsconfig.json` `paths` | module resolution — a file becomes another module |

## `package.json` scripts — the install-hook exec

```json
{ "scripts": { "preinstall": "node -e 'fetch(...)'" } }
```

If the upload lands a `package.json` where a build runs `npm install`
(deploy step, plugin loader, "install this package" feature) — the
`preinstall`/`install`/`postinstall`/`prepare` hooks execute as the
build user.

## `node_modules` write — the require() hijack

Landing a file inside `node_modules/express/index.js` or a shadow
package — `require('express')` resolves your file on the next require.
CTF shapes: upload traverses into `node_modules/`, or a "plugin" feature
drops code there. The exec needs a require — a restart or lazy-require
tick.

## The config-file-as-code sinks — `.babelrc`, `webpack.config.js`, etc.

Tool configs that `require()` code:

- `webpack.config.js` exports a function — runs on build
- `jest.config.js`/`babel.config.js` — evaluated
- `tsconfig.json` `"paths"`/`"extends"` — `extends` loads a file — a
  `extends: "../../x.json"` reaches anywhere
- `.mocharc.js`, `.eslintrc.js`, `next.config.js` — all JS configs execute

The "config" upload IS code.

## `require()` order-of-precedence — how a file shadows a builtin

```
require('x') → ./node_modules/x → ../node_modules/x → ... → core
```

A `node_modules/` deeper in the path or an `x.js` in the app root shadows
the intended module. Node's `main` field in `package.json` redirects the
require target.

## The multer/busboy temp-file dance — where upload libs put files

- `multer` default `dest` — `uploads/` or OS tmp; `filename` fn controls
  the name — a `filename` that ignores extension or trusts it blindly
  (`cb(null, file.originalname)`) writes `x.php`→`x.php`
- `formidable`/`busboy` tmpdir — files land in os.tmpdir with random
  names — `race-and-temp-files.md`
- `express-fileupload` `useTempFiles:true` → tmpdir + `mv()` — `mv()` to
  `req.body.path` without sanitize = traversal (`this was the NodeGoat/
  nodejs shape`)

## The `.js` file served vs required — two different execs

- served `.js` runs in the BROWSER (client-side) — XSS not RCE
- a `.js` landed inside the app's load path runs server-side at require —
  RCE
- a `.js` landed in a static dir = browser-side
- distinguish by WHERE the file lands, not the ext

## Falsifiers

- no `package.json`/`node_modules`/config write path AND no plugin loader
- the upload lands only in static-served dirs (browser-side at worst)

## Output to record

- which npm-shaped sink the file lands near + who triggers it
