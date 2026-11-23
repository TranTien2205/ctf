# CDN/WAF identity: awswaf

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

AWS WAF identity: 403 with Request blocked text,
x-amzn-RequestId + x-amzn-errortype headers, AWSALB/AWSELB
cookies (sticky sessions). Rate-based rules trigger on enum
speed - recon rate planning notes. awswaf token challenges
(aws-waf-token) in responses.
## Pivot

Signal harvested -> out-*; route named -> that skill.
