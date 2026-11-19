# Laravel Ignition/Whoops — PHP debug pages — checklist

Laravel's Ignition (or older Whoops) page dumps env vars, request data, and the full stack — plus a known RCE in old Ignition.

## Checklist

- [ ] Trigger an error; look for the Ignition/Whoops layout.
- [ ] Extract APP_KEY and all env values from the page.
- [ ] Old Ignition (<2.5.2) had a file_get_contents RCE — check the version.
- [ ] APP_KEY lets you decrypt cookies and forge data.

## Abort conditions

- APP_KEY is the app's encryption key — cookies, encrypted fields all fall.
- Ignition RCE needs a specific version — don't try the exploit on a modern page.
- The 'env' section includes masked-but-not-really values.

## Falsifier

Falsifier — standard Laravel error page or plain 500: debug off.
