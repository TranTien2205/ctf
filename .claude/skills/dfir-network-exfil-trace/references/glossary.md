# Glossary

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

| Term | Meaning here |
|---|---|
| Tx Bytes | `endpoints,ip` column — bytes the host transmitted (wire) |
| orig_bytes | Zeek conn.log — application payload the originator sent |
| bytes_toserver | Suricata flow — bytes in the initiator-to-responder direction |
| Initiated | Sysmon 3 — true when the local process opened the connection |
| ProcessGuid | Sysmon join key — ties event 3/22 to event 1; never PID |
| SNI | TLS ClientHello server name — a client claim, not an observation |
| Qname Len | dns,tree leaf — query-name length stats |
| conn_state | Zeek conn.log — SF/S0/REJ/RSTR... session outcome |
| history | Zeek conn.log — per-event letters, upper=originator |
| missed_bytes | Zeek conn.log — sensor-dropped payload; volume floor warning |
| flow_id | Suricata — joins alert records to flow records |
| uid | Zeek — joins conn.log to the protocol logs |
| AppId | SRUM — index into SruDbIdMapTable; resolve before quoting |
| OLE Automation date | SRUM TimeStamp type — double days since 1899-12-30 |
| WFP | Windows Filtering Platform — 5156/5157 audit events |
| ESE | Extensible Storage Engine — SRUDB/qmgr container format |
| covert channel | data carried by a field/timing, not by a payload |
| domain fronting | SNI lies; ip.dst is the truth |
| DoH/DoT | DNS inside HTTPS (443) / TLS (853) |
| beacon | periodic low-volume flow; cv of deltas is the classifier |
| jitter | deliberate cadence noise; measured as mad/median |
| data leaf | io,phs row of unrecognised payload — not proof of evil |
| follow | tshark stream reassembly; direction headers matter |
| keylog | session-key file enabling `-o tls.keylog_file:` decryption |
| claim vs observation | sender-asserted field vs what was measured |

Terms are defined by their use in this corpus; the authoritative field lists
live in each artifact's own module.
