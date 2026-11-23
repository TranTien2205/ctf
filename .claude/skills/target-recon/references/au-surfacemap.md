# Authenticated recon: surfacemap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Post-auth surface map: the endpoint list that
only exists authenticated - account/settings/admin/import/
export/api-token routes, and the parameters they take.
Auth-gated routes get the same enum budget as public ones;
an authenticated 403 on /admin is a different observation
than a 404 and both are recorded verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
