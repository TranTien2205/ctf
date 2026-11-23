# Cloud recon: awsmetadata

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

AWS metadata surface (recon-names only -
reaching it is ssrf's job): 169.254.169.254/latest/meta-data/
- iam/security-credentials/<role> = creds surface,
user-data = startup script (secrets classic), hostname/
public-keys. IMDSv2 needs PUT token = posture note.
Identifying the app fetches URLs IS the recon finding.
## Pivot

Signal harvested -> out-*; route named -> that skill.
