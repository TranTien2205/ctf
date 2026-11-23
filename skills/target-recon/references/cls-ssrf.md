# Class recheck: ssrf

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-ssrf needs: fetch-capable params
(url=, callback=, webhook, image-by-url, pdf-from-html,
import), the outbound behavior visible (does the response
embed fetched content?), internal address hints in JS/config,
and the cloud-metadata question (is this on a cloud provider
- cdn-* + headers tell).
## Pivot

Signal harvested -> out-*; route named -> that skill.
