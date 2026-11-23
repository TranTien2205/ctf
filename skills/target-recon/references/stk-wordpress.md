# Stack playbook: wordpress

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

WordPress fingerprints: /wp-content/ and /wp-includes/ asset
paths, wp- cookie prefixes, a meta generator tag, x-pingback header.

Recon checks:
- GET /wp-login.php -> login form present means WP confirmed
- GET /wp-json/wp/v2/users -> user list leak (id, name, slug) =
  userenum evidence AND the login names for later stages
- GET /?author=1 -> redirect to /author/<slug> confirms the same
- GET /xmlrpc.php -> 'XML-RPC server accepts POST requests only'
  opens pingback/brute surface
- GET /wp-content/uploads/ -> open listing = infodisclosure
- readme.html / /wp-admin/install.php left behind = version + state
- /wp-json/ root -> route map; custom plugin routes enumerated here

Predicts: userenum (wp/v2/users, ?author=), infodisclosure
(listings, backups of wp-config.php), upload themes/plugins if
creds fall later. Plugins/theme slugs in asset paths name the
attack surface to enumerate next.
## Pivot

Signal harvested -> out-*; route named -> that skill.
