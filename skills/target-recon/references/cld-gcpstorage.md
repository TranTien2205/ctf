# Cloud recon: gcpstorage

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

GCP storage: storage.googleapis.com/<bucket>
returns XML (ListBucketResult or AccessDenied) - same
tri-state observation as S3. firebaseio.com/<path>.json =
Firebase RTDB read-permission check (the classic open-db).
firestore.googleapis.com endpoints in JS = firestore
surface. Candidates from app/domain names only.
## Pivot

Signal harvested -> out-*; route named -> that skill.
