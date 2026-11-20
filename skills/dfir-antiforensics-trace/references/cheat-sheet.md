# One-page command sheet

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## The gap probe (no EVTX parser needed)

The inline python in `../SKILL.md` — reads `ElfChnk` first/last identifiers
at +0x18/+0x20 per chunk, prints `next_id, oldest, newest, gaps` per .evtx.
`oldest=1` = cleared; non-empty gaps = surgical deletion; no chunks =
truncated stub.

## The clear-and-disable sweep

```bash
python3 tools/forensics/evtx_query.py --input converted.jsonl \
    --challenge <c> \
    --event-id 1102 --event-id 104 --event-id 1100 \
    --event-id 4719 --event-id 1013
```

`matched: 0` on all five is one falsifier component.

## Event queries

```bash
# who cleared Security
python3 tools/forensics/evtx_query.py --input security.jsonl \
    --event-id 1102 --challenge <c> --answer SubjectUserName
# which non-Security channel
python3 tools/forensics/evtx_query.py --input system.jsonl \
    --event-id 104 --challenge <c> --answer Channel
# timestomp pair
python3 tools/forensics/evtx_query.py --input sysmon.jsonl \
    --event-id 2 --field-contains TargetFilename=<name> --challenge <c>
# sysmon killed
python3 tools/forensics/evtx_query.py --input sysmon.jsonl \
    --event-id 4 --event-id 16 --challenge <c>
# defender disable/purge
python3 tools/forensics/evtx_query.py --input defender.jsonl \
    --event-id 5001 --event-id 5010 --event-id 5012 \
    --event-id 5007 --event-id 1013 --event-id 5013 --challenge <c>
```

## Artifact inventory

```bash
python3 tools/forensics/artifact_inventory.py --path <bundle> --challenge <c>
```

Names registry-transaction-log / recycle-bin / Defender trees — the third
falsifier component.

## Filesystem survivors

```bash
python3 tools/forensics/recycle_i.py ...   # $I records: path + delete time
python3 tools/forensics/mft_parse.py ...   # deleted records, $SI/$FN
python3 tools/forensics/usn_parse.py ...   # $J reasons 0x8000/0x200
python3 tools/forensics/lnk_parse.py ...   # deleted-file usage history
python3 tools/forensics/hive_parse.py ...  # key LastWriteTime, values
```

## The merge

```bash
python3 tools/forensics/timeline_merge.py \
  --source clears.csv:time:clears --source survivors.csv:time:survivors \
  --challenge <c> --gap 600
```

Puts the clear events and the survivor records on one axis — the hole's
bounds are computed, not estimated.
