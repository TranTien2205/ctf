# Cloud recon: clouderrors

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Cloud error fingerprints: AWS 'The specified
key does not exist' XML, S3 AccessDenied XML, Azure
'BlobNotFound', GCP 'storage#objects' JSON, CloudFront 'The
request could not be satisfied', API Gateway {'message':
'Missing Authentication Token'} = the AWS API-GW tell.
Each body shape names the edge verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
