# Class boundary - what SSTI is not

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

SSTI is a request value reaching the TEMPLATE context, evaluated
by the engine. It is NOT: reflected XSS (the payload renders in the
page, not the template - an arithmetic marker distinguishes them),
command injection (the value reaches a shell, not an engine - the
{{7*7}} marker stays literal), or CRLF/log injection. The differential
probe decides: an arithmetic or engine-specific marker evaluated in
the response means the value reached the engine.

## Evidence chain

1. Marker probe: `{{7*7}}`-shaped -> '49' in the response where the
   raw marker would be literal elsewhere.
2. Engine differential: Jinja2 vs Twig vs Freemarker markers that
   only ONE engine evaluates - names the engine before the chain.
3. Context: string interpolation vs template-block context changes
   which payload grammar applies.

## Pivot

Boundary applies -> web-command-injection (shell-boundary value) or
web-xss (render-boundary value).
