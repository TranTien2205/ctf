# Ruby Deserialization — Marshal + Psych/YAML

## Marshal — `\x04\x08` then a typed object stream

```
\x04\x08          version 4.8 marker
o:                object   O   object-with-ivars
u:                usermarshal (marshal_dump/marshal_load)
U:                userdef (_dump/_load)
I                 ivars wrapper
:                 symbol   ;    symbol link
"                 string
i                 integer
[                 array    {    hash
S:                struct   c    class   m    module   e    extended
```

`Marshal.load` instantiates classes and calls their load hooks — the same
"constructor of a chosen class" primitive every deserializer gives.

## The two trigger hooks

| Hook | Fires when | Use |
|---|---|---|
| `marshal_load(data)` | class defines `_load`/`marshal_load` and appears as `u:`/`U:` | arbitrary code in the hook |
| `_load(str)` | `U:` type | same |
| `initialize` | indirectly via object construction | weaker |
| `method_missing` | a dispatched call inside a gadget | chain-internal pivot |

## The universal ERB→gadget chain shape

The classic Rails/Ruby RCE (the "universal" gadgets) walks:

```
ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy
  → @instance = ERB object with @src = "attacker code"
  → @method = :result
  → Deprecation proxies send the method to the ERB instance
  → ERB#result evaluates @src → your Ruby runs
```

Versioned variants swap the entry class — `Gem::Requirement`,
`ActiveSupport::Deprecation`, `Gem::Package::TarReader`, `Net::WriteAdapter`
combos — the mechanism is always *a trusted object graph whose traversal
ends in an eval-into-src or system-call.*

## Building the universal payload

```ruby
# the shape (concept — use a maintained generator for the real bytes)
# rails_rce / universal-rce scripts emit the Marshal stream for a target
# Rails/Ruby version — hand-constructing the ivar graph is fragile
```

```bash
# metasploit carries maintained gadgets:
msfconsole -q -x "use exploit/multi/http/secretwetpy_installer_rce; help"
# the reusable Ruby script (verify against target Ruby/Rails):
# https://github.com/... universal_rce.rb  — emits the \x04\x08 stream
```

The practical recipe: detect Rails version (error page, `Gemfile.lock` in
source, `X-Powered-By`), pick the universal chain variant for that range,
Marshal-dump the assembled proxy graph, base64 → cookie/param.

## Psych / YAML — the typed-tag path

```
--- !ruby/object:Gem::Installer
i: x
--- !ruby/object:ActiveSupport::Deprecation
```

`YAML.load`/`Psych.load` instantiate `!ruby/object:X` classes — same gadget
chains as Marshal, different container. `YAML.safe_load` permits only
`Symbol`, `Date`, `Time`, `Range`, `Regexp`… unless `permitted_classes` adds
more — a `Symbol`-only safe_load still can't reach an arbitrary class.

```ruby
# vulnerable:
YAML.load(user_input)            # Psych < 4 defaults unsafe
Psych.load(user_input)
# safe:
YAML.safe_load(user_input)                        # basic types only
YAML.safe_load(user_input, permitted_classes:[User]) # whitelisted
```

### The ERB-via-YAML shape

```yaml
--- !ruby/object:ERB
src: "<%= `id` %>"
```

— only fires if something calls `erb.result`. The real chains embed the ERB
inside a `DeprecatedInstanceVariableProxy` so a later method call triggers it.

## Second-order Ruby sinks

- **Rails session cookie** (Marshal) — `Rails.application.config.session_store
  :cookie_store` serializes the session with Marshal under an HMAC. You need
  `secret_key_base` to forge. If the key leaks (source, `config/secrets.yml`,
  env, error page) → full Marshal RCE via cookie.
- **Sidekiq/Resque job payload** — the job class + args are Marshal'd/JSON'd;
  an attacker-writable job enqueues a gadget.
- **Rails cache** — `Rails.cache` Marshal's values; a write to the cache
  poisons the next read.
- **`dbm`/`PStore`** file the app re-opens.

## The falsifier set

- `Marshal.load` only ever runs on server-generated blobs (signed cookie
  with unleaked `secret_key_base`) → key-attack problem, not grammar.
- `YAML.safe_load` with no `permitted_classes` that name a gadget class.
- Opaque JSON blob — no `!ruby/` tag, no `\x04\x08`.

## Detection recap

```bash
# base64 cookie → \x04\x08 = Marshal, --- !ruby/ = Psych
echo -n "$BLOB" | base64 -d | xxd | head -2
# corrupted \x04\x08 → ArgumentError: dump format error = parser reached
```

## Output to record

- Marshal vs Psych + Ruby/Rails version that selects the chain
- The universal-chain variant name and the verbatim response
- Whether the channel was direct or second-order (session/job/cache)
