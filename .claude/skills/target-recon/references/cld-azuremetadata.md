# Cloud recon: azuremetadata

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Azure metadata: 169.254.169.254/metadata/
instance?api-version= - requires Metadata: true header =
posture. /metadata/identity/oauth2/token = MSI token
surface. App Service env surfaces: /home/site/wwwroot,
WEBSITE_* hints in errors. Named for ssrf payload lists.
## Pivot

Signal harvested -> out-*; route named -> that skill.
