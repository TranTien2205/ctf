# Stack playbook: nginxstatic

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

nginx serving static/reverse-proxy only:
server: nginx, static assets, proxy_pass to an app (404 vs
app-specific error pages reveal the boundary).

Recon checks:
- Which paths proxy vs serve static - error page style
  changes at the boundary = topology map
- alias/traversal misconfigs (/static../ -> alias escape)
- autoindex on for upload/listing dirs
- X-Accel-Redirect handling -> internal-file surface
- proxy_hide_header gaps -> header surfaces

Predicts: alias traversal (file-read), smuggling at
proxy boundary, parser-differential, cache deception.
## Pivot

Signal harvested -> out-*; route named -> that skill.
