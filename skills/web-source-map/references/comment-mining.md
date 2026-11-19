# Comment mining — the notes devs leave in source

## Why comments are gold

Recovered `sourcesContent` carries the original *comments* — `// TODO`,
`// FIXME`, `// secret`, `// remove before prod`, `// flag{`. Devs leave
notes, credentials, and the flag in source; the map leaks them verbatim.
A minified bundle strips comments, but a recovered source keeps them.

## The comment grep set

```bash
# the classic markers
grep -rniE '//\s*(TODO|FIXME|HACK|BUG|XXX|NOTE|WARN|SECRET|PASSWORD|KEY|FLAG|ADMIN|INTERNAL|DEBUG|REMOVE|HARDCODE|TEMP|DEV)' recovered/
# the flag shape in any comment
grep -rnoE 'flag\{[^}]*\}|ctf\{[^}]*\}|CTF\{[^}]*\}' recovered/
# a credential in a comment
grep -rniE '//.*(password|secret|token|key|cred|login)\s*[:=]' recovered/
# a URL/host in a comment
grep -rnoE '//.*(https?://|internal\.|\.svc|\.local)' recovered/
```

## The comment shapes

| Shape | Means |
|---|---|
| `// TODO: remove before prod` | a dev left a test/debug path |
| `// FIXME: hardcoded` | a hardcoded value — often a credential |
| `// secret:`, `// key:` | a named credential |
| `// flag{` | the flag itself |
| `// internal only`, `// admin` | a gated surface note |
| `/* disabled */` + code | dead code that may still run server-side |
| `// backend does not check` | a client-side gate note — a real lead |

## The flag-in-comment pattern

A very common CTF shape: the flag is a comment in the shipped source —
`// flag{...}`, a `const FLAG`, an env-inlined flag. It is still a
*candidate*: `pre-flag` it, prove it against a live/artifact response.

## The `console.log` / debug print

```bash
grep -rniE 'console\.(log|debug|warn|error)\(' recovered/
```

A `console.log('secret:', x)` or `console.log(token)` in shipped source
leaks the value — a secret left in a debug print.

## The comment → lead chain

A comment names intent the code hides — `// this hits /internal/dump`,
`// the key is in config`. Read the comment's context (`--context`/
`-A3 -B3`); it often names the exact endpoint or secret the surrounding
code uses.
