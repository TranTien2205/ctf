# -EncodedCommand — the base64 carve

`-e`, `-ec`, `-enc` all bind to EncodedCommand — match `-e` plus the
base64 blob, decode UTF-16LE. Classic 400 `HostApplication` recovers
it when script-block logging is off; PEL wraps 4104 in CMS.

## -e

All prefixes bind; decode UTF-16LE.

## The blob

-e/-ec/-enc + base64, UTF-16LE.
