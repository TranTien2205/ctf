# Cloud recon: s3buckets

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

S3/bucket discovery: <name>.s3.amazonaws.com,
s3.<region>.amazonaws.com/<name>, <name>.s3-website-* hosts
referenced in JS/DNS. List-bucket posture: GET returns XML
ListBucketResult (open = inventory) vs AccessDenied (exists,
closed) vs NoSuchBucket (absent) - three different
observations. Candidates: domain fragments, app name,
dev/stage/prod suffixes - bounded list only.
## Pivot

Signal harvested -> out-*; route named -> that skill.
