# Attack trees — the branching probe space, pruned

The class's decision space as a tree — each branch a falsifiable
arm, each leaf a verdict. Walk it top-down; close branches with
falsifiers rather than re-probing.

---

## 1. The master tree

```
P0 does a merge/path-setter/rename exist that takes request data?
├─ no  → not this class — park, pivot (mass-assignment/deser/nosqli)
└─ yes
   P1 does the input reach the sink as an OBJECT (not a scalar)?
   ├─ no → wrong carrier — find the object-carrying field
   └─ yes
      P2 does a KEY-LEVEL write reach a shared root?
      │  arms: __proto__ | constructor.prototype | __class__ |
      │        $rename path | set(path) | setattr magic names
      ├─ all refute → merge is guarded — FALSIFIER, park
      └─ one confirms
         P3 does the write LAND on the shared root (fresh-obj oracle)?
         ├─ own-property only → mass-assignment, not PP — refute
         └─ shared write
            P4 does a SINK read a fallback for a writable name?
            │  arms: authz names | template opts | spawn/env |
            │        require | url | config | toJSON/then/inspect
            ├─ no sink → data corruption at most — record, park
            └─ sink found
               P5 harmless marker → does behavior change?
               ├─ no → read is own-only/different path — refute
               └─ yes → CONFIRMED write+sink — escalate to payoff
```

## 2. The carrier sub-tree (P1)

```
carrier?
├─ JSON body          {"__proto__":{...}} / nested / constructor
├─ query string        ?__proto__[m]=1 / ?a[__proto__][m]=1
├─ urlencoded form     __proto__[m]=1 in POST body
├─ path-API field      {"field":"__proto__.m","value":1}
├─ update document     {"$rename":{"a":"__proto__.m"}} /
│                      {"$set":{"__proto__.m":1}}
├─ header reparse      X-Custom: {"__proto__":{...}} (app JSON-parses)
├─ cookie JSON         session={"__proto__":{...}} (app parses)
├─ multipart field     a file-field whose text is parsed as JSON
├─ websocket message   ws.send({"__proto__":{...}})
├─ GraphQL input       {input:{__proto__:{...}}} into a merge
└─ URL fragment        #{"__proto__":{...}} (client-side merge)
```

Order: JSON body first (richest objects), then qs, then path-API,
then update-doc, then the exotics. Each carrier is one probe —
a confirmed carrier opens the key-level tree for that carrier.

## 3. The key sub-tree (P2)

```
key?
├─ __proto__                  flat + nested
├─ constructor.prototype      flat + nested  (+double-nest variants)
├─ \u005f\u005fproto\u005f\u005f  escaped spelling
├─ proto                      app-defined shorthand
├─ prototype                  bare (function targets)
├─ __class__ / __init__ / __globals__   (Python merge/setattr)
├─ __dict__.update            (Python namespace swap)
├─ field:"__proto__.x"        (dotted path-API)
├─ $rename:"x->__proto__.m"   (document-store operator)
└─ $set:"__proto__.m"         (same store, set op)
```

`refutes` across ALL arms = the merge is guarded — the whole
class-branch closes; record the falsifier and stop iterating.

## 4. The sink sub-tree (P4)

```
sink reads a polluted name?
├─ authz    isAdmin/is_admin/role/level/verified/owner_id/tenant_id
├─ ejs      outputFunctionName/localsName/destructureLocals/escape
├─ pug      name/filename/basedir/filters/globals/self
├─ hbs      compat/allowProto*/extensions/helpers/partials
├─ njk      autoescape/globals/filters/extensions/loader
├─ mustache partials/tags/delimiters
├─ _tpl     variable/imports/sourceURL/evaluate/interpolate/escape
├─ spawn    shell/env/argv0/cwd/uid/gid/detached/stdio
├─ fork     modulePath/execPath/execArgv/env/silent/workerData
├─ require  main/paths/extensions/module/specifier/dir
├─ fetch    url/uri/hostname/baseURL/proxy/headers/agent
├─ config   debug/dev/verbose/secret/key/views/"view engine"
├─ json     toJSON/inspect/then/valueOf/toString/constructor
├─ py       SECRET_KEY/DEBUG/FLAG/os.environ keys/class attrs
└─ client   src/href/innerHTML/ADD_TAGS/ADD_ATTR/ALLOWED_*/FORBID_*
```

Each is ONE named probe against the discovered sink — the sink's
name list is the write vocabulary.

## 5. The payoff sub-tree (P5+)

```
confirmed write+sink → what does the sink buy?
├─ authz bypass      → read the gated endpoint/data
├─ template embed    → generated-code exec → RCE
├─ spawn env         → NODE_OPTIONS/LD_PRELOAD → child RCE
├─ require path      → load attacker module → RCE
├─ shell:true        → cmd-inj in the spawned command
├─ url/callback      → SSRF to internal/attacker
├─ config secret     → signing-key reuse → session forge
├─ toJSON/exec       → exec-at-serialize primitive
├─ then              → promise-resolution primitive
├─ os.environ        → env-read sinks → python RCE
└─ client sinks      → XSS (script src / sanitizer opts / handler)
```

The payoff is the chain — `pollution-to-rce.md` and
`pollution-to-xss.md` carry the gadget detail.

## 6. The pruning rules

- A `refutes` on ALL carriers closes P1 → the site isn't merge-
  reachable; do NOT retry carriers with fancier encodings (that's
  a P2 variant, not a new carrier).
- A `refutes` on ALL keys for a confirmed carrier closes P2 for
  that carrier — try the NEXT carrier's key set, not the same
  keys again.
- A confirmed write with NO sink close P4 → park as "data
  corruption primitive" — it's a capability, not a vuln yet.
- A confirmed sink-read with a harmless marker closes P5 → the
  impact path is proven; the payoff probe is the LAST step.

## 7. Budget mapping

Per the controller: each branch gets ~5 probes / 15 minutes. The
tree has 5 levels; a disciplined walk needs ~15-25 probes total.
If a level's arms are exhausted, park THAT level's hypothesis
(`--result refutes --status parked`) and try the next branch —
never iterate within a refuted arm.

## 8. Ledger shape

```bash
python3 tools/state.py <c> --hypothesis "carrier:json-body" 
python3 tools/state.py <c> --hypothesis-id <id> --result confirms --status proven
python3 tools/state.py <c> --hypothesis "key:constructor.prototype"
python3 tools/state.py <c> --hypothesis-id <id> --result refutes --status parked
python3 tools/state.py <c> --hypothesis "key:__proto__"
python3 tools/state.py <c> --hypothesis-id <id> --result confirms --status proven
python3 tools/state.py <c> --hypothesis "sink:ejs-outputFunctionName"
```
