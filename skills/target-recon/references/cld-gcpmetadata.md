# Cloud recon: gcpmetadata

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

GCP metadata surface: metadata.google.internal
/computeMetadata/v1/ - requires Metadata-Flavor: Google
header = posture marker; instance/service-accounts/default/
token = the creds surface, attributes/ = startup scripts.
Named for the ssrf payload list when a fetch surface exists.
## Pivot

Signal harvested -> out-*; route named -> that skill.
