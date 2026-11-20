# 4624 field anatomy — what answers what

`IpAddress`/`IpPort` where-from, `WorkstationName` source host,
`AuthenticationPackageName`/`LmPackageName`/`KeyLength` the method,
`TargetLogonId`/`TargetLinkedLogonId` the join and split-token pair,
`ElevatedToken`/`LogonProcessName`/`ProcessName` the privilege and
requesting binary.

## The anatomy

Ip/Workstation/Package/LogonId/Elevated/ProcessName.

## The read

Type first, then the join key.
