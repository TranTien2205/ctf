# Laravel Ignition/Whoops — PHP debug pages — deep

Laravel's Ignition (or older Whoops) page dumps env vars, request data, and the full stack — plus a known RCE in old Ignition.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — standard Laravel error page or plain 500: debug off.

## Highest-cost traps

- APP_KEY is the app's encryption key — cookies, encrypted fields all fall.
- Ignition RCE needs a specific version — don't try the exploit on a modern page.
- The 'env' section includes masked-but-not-really values.

## Commands

```bash
curl -s '$BASE/bad' | grep -iE 'ignition|whoops|laravel'
```

## Cross-references

`framework-debug.md` · `env-config-leaks.md`
