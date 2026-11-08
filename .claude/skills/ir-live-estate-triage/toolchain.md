# What is installed, and what the method has to be built around

Opened from `SKILL.md` once the service is back up and the chain has to be
reconstructed. Measured on this box; re-measure with `command -v` before
relying on any row.

Measured on this box. Build the method around this, not around a tool you wish you
had:

| Available | Absent, so do not plan on it |
|---|---|
| `fls`, `mactime`, `icat`, `tsk_recover` (filesystem timeline and file recovery) | `plaso` / `log2timeline` |
| `bulk_extractor` (strings and carving at scale) | `volatility3` — **memory images cannot be analysed here at all** |
| `dumpcap`, `tshark`, `scapy` | `suricata`, `zeek` |
| `journalctl`, the text logs themselves | `auditctl` / `ausearch`, so no audit trail |
| `tools/forensics/timeline_merge.py`, `tools/forensics/artifact_inventory.py` | a Windows EVTX parser — `python-evtx` and `evtx_dump` are both absent, so `tools/forensics/evtx_query.py` degrades to `verdict=inconclusive` |

If the estate turns out to be Windows-heavy, that last row is the binding
constraint and installing an EVTX parser is the single highest-value install of the
contest. Say so out loud rather than working around it silently.

Merge whatever you do have into one ordered timeline:

```bash
python3 tools/forensics/timeline_merge.py --challenge <name> \
        --source /evidence/logs/access.log:0:web \
        --source bodyfile.csv:1:fs --contains <indicator> --limit 200
```

