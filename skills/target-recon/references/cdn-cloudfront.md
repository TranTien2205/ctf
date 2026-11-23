# CDN/WAF identity: cloudfront

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

CloudFront identity: x-amz-cf-id, x-amz-cf-pop,
via: CloudFront, x-cache (Hit/Miss from cloudfront). Predicts:
S3/ALB origin behind, cache-key behavior class, signed-URL
surfaces. A 'The request could not be satisfied' error page
is the fingerprint - verbatim recorded.
## Pivot

Signal harvested -> out-*; route named -> that skill.
