# LOLBAS — Image is the signed binary

certutil/mshta/rundll32/wmic/bitsadmin/msiexec/forfiles — the signed
binary is `Image`, the payload is `CommandLine` and the parent-child
pair. `wmic process call create` parents to `WmiPrvSE.exe`; BITS'
network belongs to `svchost.exe`.

## The pair

Signed Image + payload CommandLine + odd parent.

## Parent

wmic -> WmiPrvSE; BITS -> svchost.
