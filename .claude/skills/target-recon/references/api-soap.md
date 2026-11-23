# API recon: soap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SOAP recon: ?wsdl on every discovered service path
(/?wsdl, /service?wsdl, /services?wsdl, /ws/service.asmx?wsdl).
The WSDL enumerates operations, params, and types in one
document = surface map. .asmx/.svc/.wsdl extensions and
text/xml+SOAPAction headers confirm the stack. WS-Security
headers noted for the auth picture.
## Pivot

Signal harvested -> out-*; route named -> that skill.
