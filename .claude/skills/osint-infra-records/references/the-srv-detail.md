# SRV — named services

`_sip._tcp`, `_xmpp`, `_ldap` etc — service discovery; a service
hostname leaks. Try the common service names.

## The form

`_service._proto.domain` — e.g. `_sip._tcp.example.com` SRV →
`sip-server.example.com:5060`. Common services: sip, xmpp, ldap,
kerberos, matrix.
