# Stack playbook: coldfusion

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ColdFusion: .cfm/.cfc extensions, CFID/CFTOKEN
cookie pair, /CFIDE/ admin tree, 'ColdFusion' in errors or
Server header.

Recon checks:
- /CFIDE/administrator/ -> admin login = default surface
- /CFIDE/componentutils/ -> cfcexplorer = component leak
- Application.cfc / .cfm source via backup probes
- fusebox/mach-ii URL conventions (fuseaction=)
- Error 'coldfusion.' stack -> version + path leak

Predicts: deserialization (flash remoting), sqli, LFI in
.cfm params, admin-console route.
## Pivot

Signal harvested -> out-*; route named -> that skill.
