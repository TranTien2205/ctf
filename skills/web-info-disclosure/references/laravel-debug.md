# Laravel Ignition/Whoops — PHP debug pages

Laravel's Ignition (or older Whoops) page dumps env vars, request data, and the full stack — plus a known RCE in old Ignition.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Ignition-styled error page | debug on | env vars in page |
| APP_KEY visible | encryption key | decrypt/forge data |
| env section | all env vars | secrets harvest |
| solution cards / execute button | interactive fix | RCE boundary |

## Steps

1. Trigger an error; look for the Ignition/Whoops layout.
2. Extract APP_KEY and all env values from the page.
3. Old Ignition (<2.5.2) had a file_get_contents RCE — check the version.
4. APP_KEY lets you decrypt cookies and forge data.

## Falsifier

Falsifier — standard Laravel error page or plain 500: debug off.

## Traps

- APP_KEY is the app's encryption key — cookies, encrypted fields all fall.
- Ignition RCE needs a specific version — don't try the exploit on a modern page.
- The 'env' section includes masked-but-not-really values.

## Commands

```bash
curl -s '$BASE/bad' | grep -iE 'ignition|whoops|laravel'
```

## Cross-references

`framework-debug.md` · `env-config-leaks.md`
