# Stack playbook: phpgeneric

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Generic PHP: .php extensions, PHPSESSID,
X-Powered-By: PHP/x.y.z, Apache or nginx+php-fpm.

Recon checks:
- /phpinfo.php -> config + env leak (common CTF fixture)
- index.php~ index.php.bak .swp -> source leak
- /vendor/ exposure -> composer deps = gadget inventory
- PHP version -> exploit matrix for the version
- disable_functions hint in phpinfo -> command-execution class
- .htaccess/.htpasswd readable -> config leak

Predicts: sqli, file-upload, LFI/RFI (file-read-primitives),
deserialization on unserialize cookies, cmdi.
## Pivot

Signal harvested -> out-*; route named -> that skill.
