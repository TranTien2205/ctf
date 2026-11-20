# Windows Event Logs — EVTX

Binary format — evtx_dump/EvtxECmd convert to XML/JSON, then treat
like a log. Event IDs: 4624/4625 logons, 4688 process, 7045 service.

## The Event-ID map

- 4624 logon success, 4625 logon failure
- 4634/4647 logoff
- 4688 process creation (with command line)
- 4697 / 7045 service install — persistence
- 4720 account created, 4732 added to group
- 4776 NTLM credential validation
- 1102 log cleared — anti-forensics

Convert, then grep the EventID + the surrounding fields.
